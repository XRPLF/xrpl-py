"""Integration test for reserve-sponsored trust lines.

When a trust line's owner reserve is sponsored (the trust-line owner submits a
TrustSet carrying ``sfSponsor`` + the ``spfSponsorReserve`` flag, co-signed by
the sponsor), the resulting RippleState ledger object records the sponsor via
``sfHighSponsor`` / ``sfLowSponsor`` (the side depends on which of the two
accounts is the numerically-higher address).
"""

from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    LEDGER_ACCEPT_REQUEST,
    fund_wallet_async,
    test_async_and_sync,
)
from xrpl.asyncio.transaction import autofill, submit
from xrpl.asyncio.transaction.main import sign
from xrpl.models import TrustSet
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.requests.ledger_entry import LedgerEntry, RippleState
from xrpl.models.response import ResponseStatus
from xrpl.transaction import sign_as_sponsor
from xrpl.wallet import Wallet

# Sponsor-type flags.
_TF_SPONSOR_RESERVE = 0x00000002


class TestSponsorTrustlineReserve(IntegrationTestCase):
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
