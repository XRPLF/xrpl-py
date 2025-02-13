from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import WALLET
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.requests import AccountLines, AccountObjects
from xrpl.models.transactions import TrustSet, TrustSetFlag
from xrpl.wallet import Wallet

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
