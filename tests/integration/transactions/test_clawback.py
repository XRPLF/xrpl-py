from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    fund_wallet,
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import WALLET
from xrpl.models import (
    AccountSet,
    AccountSetAsfFlag,
    Clawback,
    IssuedCurrencyAmount,
    MPTAmount,
    Payment,
    TrustSet,
    TrustSetFlag,
)
from xrpl.models.requests import LedgerEntry, Tx
from xrpl.models.requests.ledger_entry import MPToken
from xrpl.models.transactions import (
    MPTokenAuthorize,
    MPTokenIssuanceCreate,
    MPTokenIssuanceCreateFlag,
)
from xrpl.wallet import Wallet

HOLDER = Wallet.create()
fund_wallet(HOLDER)


class TestClawback(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        # test setup

        await sign_and_reliable_submission_async(
            AccountSet(
                account=WALLET.classic_address,
                set_flag=AccountSetAsfFlag.ASF_ALLOW_TRUSTLINE_CLAWBACK,
            ),
            WALLET,
        )

        await sign_and_reliable_submission_async(
            TrustSet(
                account=HOLDER.classic_address,
                flags=TrustSetFlag.TF_SET_NO_RIPPLE,
                limit_amount=IssuedCurrencyAmount(
                    issuer=WALLET.classic_address,
                    currency="USD",
                    value="1000",
                ),
            ),
            HOLDER,
        )

        await sign_and_reliable_submission_async(
            Payment(
                account=WALLET.classic_address,
                destination=HOLDER.classic_address,
                amount=IssuedCurrencyAmount(
                    currency="USD", issuer=WALLET.classic_address, value="1000"
                ),
            ),
            WALLET,
        )

        # actual test - clawback
        response = await sign_and_reliable_submission_async(
            Clawback(
                account=WALLET.classic_address,
                amount=IssuedCurrencyAmount(
                    issuer=HOLDER.classic_address,
                    currency="USD",
                    value="100",
                ),
            ),
            WALLET,
            client,
        )
        self.assertTrue(response.is_successful())

    @test_async_and_sync(globals())
    async def test_mptoken(self, client):
        wallet2 = Wallet.create()
        await fund_wallet_async(wallet2)

        tx = MPTokenIssuanceCreate(
            account=WALLET.classic_address,
            flags=MPTokenIssuanceCreateFlag.TF_MPT_CAN_CLAWBACK,
        )

        create_res = await sign_and_reliable_submission_async(
            tx,
            WALLET,
            client,
        )

        self.assertTrue(create_res.is_successful())
        self.assertEqual(create_res.result["engine_result"], "tesSUCCESS")

        tx_hash = create_res.result["tx_json"]["hash"]

        tx_res = await client.request(Tx(transaction=tx_hash))
        mpt_issuance_id = tx_res.result["meta"]["mpt_issuance_id"]

        auth_tx = MPTokenAuthorize(
            account=wallet2.classic_address,
            mptoken_issuance_id=mpt_issuance_id,
        )

        auth_res = await sign_and_reliable_submission_async(
            auth_tx,
            wallet2,
            client,
        )

        self.assertTrue(auth_res.is_successful())
        self.assertEqual(auth_res.result["engine_result"], "tesSUCCESS")

        await sign_and_reliable_submission_async(
            Payment(
                account=WALLET.classic_address,
                destination=wallet2.classic_address,
                amount=MPTAmount(
                    mpt_issuance_id=mpt_issuance_id, value="9223372036854775807"
                ),
            ),
            WALLET,
        )

        ledger_entry_res = await client.request(
            LedgerEntry(
                mptoken=MPToken(
                    mpt_issuance_id=mpt_issuance_id, account=wallet2.classic_address
                )
            )
        )
        self.assertEqual(
            ledger_entry_res.result["node"]["MPTAmount"], "9223372036854775807"
        )

        # actual test - clawback
        response = await sign_and_reliable_submission_async(
            Clawback(
                account=WALLET.classic_address,
                amount=MPTAmount(
                    mpt_issuance_id=mpt_issuance_id,
                    value="500",
                ),
                holder=wallet2.classic_address,
            ),
            WALLET,
            client,
        )

        self.assertTrue(response.is_successful())
        self.assertEqual(auth_res.result["engine_result"], "tesSUCCESS")

        ledger_entry_res = await client.request(
            LedgerEntry(
                mptoken=MPToken(
                    mpt_issuance_id=mpt_issuance_id, account=wallet2.classic_address
                )
            )
        )
        self.assertEqual(
            ledger_entry_res.result["node"]["MPTAmount"], "9223372036854775307"
        )
