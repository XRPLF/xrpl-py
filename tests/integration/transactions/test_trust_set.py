from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    LEDGER_ACCEPT_REQUEST,
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import WALLET
from xrpl.asyncio.transaction import autofill, submit
from xrpl.asyncio.transaction.main import sign
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.requests import AccountLines, AccountObjects
from xrpl.models.requests.ledger_entry import LedgerEntry, RippleState
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import TrustSet, TrustSetFlag
from xrpl.transaction import sign_as_sponsor
from xrpl.wallet import Wallet

# Sponsor-type flag: the sponsor covers the object's owner reserve.
_TF_SPONSOR_RESERVE = 0x00000002

LSF_LOW_DEEP_FREEZE = 0x02000000
LSF_HIGH_DEEP_FREEZE = 0x04000000


class TestTrustSet(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        issuer_wallet = Wallet.create()
        await fund_wallet_async(issuer_wallet)
        response = await sign_and_reliable_submission_async(
            TrustSet(
                account=WALLET.address,
                flags=TrustSetFlag.TF_SET_NO_RIPPLE,
                limit_amount=IssuedCurrencyAmount(
                    issuer=issuer_wallet.address,
                    currency="USD",
                    value="100",
                ),
            ),
            WALLET,
            client,
        )
        self.assertTrue(response.is_successful())
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

    @test_async_and_sync(globals())
    async def test_special_chars_curr_codes(self, client):
        issuer_wallet = Wallet.create()
        await fund_wallet_async(issuer_wallet)
        response = await sign_and_reliable_submission_async(
            TrustSet(
                account=WALLET.address,
                flags=TrustSetFlag.TF_SET_NO_RIPPLE,
                limit_amount=IssuedCurrencyAmount(
                    issuer=issuer_wallet.address,
                    currency="$$$",
                    value="100",
                ),
            ),
            WALLET,
            client,
        )
        self.assertTrue(response.is_successful())
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        response = await sign_and_reliable_submission_async(
            TrustSet(
                account=WALLET.address,
                flags=TrustSetFlag.TF_SET_NO_RIPPLE,
                limit_amount=IssuedCurrencyAmount(
                    issuer=issuer_wallet.address,
                    currency="^%#",
                    value="100",
                ),
            ),
            WALLET,
            client,
        )
        self.assertTrue(response.is_successful())
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        response = await sign_and_reliable_submission_async(
            TrustSet(
                account=WALLET.address,
                flags=TrustSetFlag.TF_SET_NO_RIPPLE,
                limit_amount=IssuedCurrencyAmount(
                    issuer=issuer_wallet.address,
                    currency="a1@",
                    value="100",
                ),
            ),
            WALLET,
            client,
        )
        self.assertTrue(response.is_successful())
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # currency codes must have exactly 3 characters
        with self.assertRaises(XRPLModelException) as error:
            TrustSet(
                account=WALLET.address,
                flags=TrustSetFlag.TF_SET_NO_RIPPLE,
                limit_amount=IssuedCurrencyAmount(
                    issuer=issuer_wallet.address,
                    currency="abcd",
                    value="100",
                ),
            )
        self.assertEqual(
            error.exception.args[0],
            "{'currency': 'Invalid currency abcd'}",
        )

    @test_async_and_sync(globals())
    async def test_deep_freeze_functionality(self, client):
        issuer_wallet = Wallet.create()
        await fund_wallet_async(issuer_wallet)

        # fresh wallet to test the specific trustline
        dest_wallet = Wallet.create()
        await fund_wallet_async(dest_wallet)

        response = await sign_and_reliable_submission_async(
            TrustSet(
                account=dest_wallet.address,
                flags=TrustSetFlag.TF_SET_FREEZE | TrustSetFlag.TF_SET_DEEP_FREEZE,
                limit_amount=IssuedCurrencyAmount(
                    issuer=issuer_wallet.address,
                    currency="USD",
                    value="100",
                ),
            ),
            dest_wallet,
            client,
        )

        self.assertTrue(response.is_successful())

        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        account_lines_response = await client.request(
            AccountLines(
                account=dest_wallet.address,
            )
        )

        self.assertTrue(account_lines_response.result["lines"][0]["deep_freeze"])

        account_objects_response = await client.request(
            AccountObjects(
                account=dest_wallet.address,
            )
        )

        self.assertTrue(
            (
                account_objects_response.result["account_objects"][0]["Flags"]
                & (LSF_LOW_DEEP_FREEZE | LSF_HIGH_DEEP_FREEZE)
            )
            != 0
        )

    @test_async_and_sync(
        globals(), ["xrpl.transaction.autofill", "xrpl.transaction.submit"]
    )
    async def test_reserve_sponsor_trust_line(self, client):
        """Sponsor covers the owner reserve of a sponsee's trust line; the
        RippleState records the sponsor via sfHighSponsor / sfLowSponsor."""
        issuer_wallet = Wallet.create()
        sponsee_wallet = Wallet.create()
        sponsor_wallet = Wallet.create()
        await fund_wallet_async(issuer_wallet)
        await fund_wallet_async(sponsee_wallet)
        await fund_wallet_async(sponsor_wallet)

        # Sponsee opens a trust line whose owner reserve is covered by the sponsor.
        trust_set = TrustSet(
            account=sponsee_wallet.address,
            limit_amount=IssuedCurrencyAmount(
                currency="USD",
                issuer=issuer_wallet.address,
                value="1000",
            ),
            sponsor=sponsor_wallet.address,
            sponsor_flags=_TF_SPONSOR_RESERVE,
        )
        autofilled = await autofill(trust_set, client)

        # Sponsee signs first, then the sponsor co-signs.
        sponsee_signed = sign(autofilled, sponsee_wallet)
        sponsor_result = sign_as_sponsor(sponsor_wallet, sponsee_signed)

        response = await submit(sponsor_result.tx, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")
        await client.request(LEDGER_ACCEPT_REQUEST)

        # Read the RippleState (trust line) and confirm the sponsor is recorded on
        # the sponsee's side (High or Low, depending on address ordering).
        ledger_response = await client.request(
            LedgerEntry(
                ripple_state=RippleState(
                    accounts=[sponsee_wallet.address, issuer_wallet.address],
                    currency="USD",
                )
            )
        )
        self.assertTrue(
            ledger_response.is_successful(),
            f"LedgerEntry failed: {ledger_response.result}",
        )
        node = ledger_response.result["node"]
        self.assertEqual(node["LedgerEntryType"], "RippleState")

        # A RippleState has two sides, and the sponsor is recorded on the side
        # belonging to the *owner* of the reserve -- the sponsee. rippled picks
        # the field by comparing the owner against HighLimit/LowLimit's issuer
        # (getLedgerEntrySponsorField), so derive the expected side the same way
        # rather than accepting either. The unexpected side must stay absent.
        high_account = node["HighLimit"]["issuer"]
        low_account = node["LowLimit"]["issuer"]
        self.assertIn(sponsee_wallet.address, (high_account, low_account))

        if high_account == sponsee_wallet.address:
            expected_field, other_field = "HighSponsor", "LowSponsor"
        else:
            expected_field, other_field = "LowSponsor", "HighSponsor"

        self.assertEqual(
            node.get(expected_field),
            sponsor_wallet.address,
            f"sponsor should be recorded in {expected_field}; node={node}",
        )
        self.assertNotIn(other_field, node)
