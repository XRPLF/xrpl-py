from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import WALLET
from xrpl.models.requests.account_objects import AccountObjects, AccountObjectType
from xrpl.models.requests.tx import Tx
from xrpl.models.transactions import (
    MPTokenAuthorize,
    MPTokenAuthorizeFlag,
    MPTokenIssuanceCreate,
    MPTokenIssuanceCreateFlag,
)
from xrpl.wallet.main import Wallet


class TestMPTokenAuthorize(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        tx = MPTokenIssuanceCreate(
            account=WALLET.classic_address,
            flags=MPTokenIssuanceCreateFlag.TF_MPT_REQUIRE_AUTH,
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

        # confirm MPTokenIssuance ledger object was created
        account_objects_response = await client.request(
            AccountObjects(account=WALLET.address, type=AccountObjectType.MPT_ISSUANCE)
        )

        # subsequent integration tests (sync/async + json/websocket) add one
        # MPTokenIssuance object to the account
        self.assertTrue(len(account_objects_response.result["account_objects"]) > 0)

        wallet2 = Wallet.create()
        await fund_wallet_async(wallet2)

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

        # confirm MPToken ledger object was created
        account_objects_response2 = await client.request(
            AccountObjects(account=wallet2.address, type=AccountObjectType.MPTOKEN)
        )

        # subsequent integration tests (sync/async + json/websocket) add one
        # MPToken object to the account
        self.assertTrue(len(account_objects_response2.result["account_objects"]) > 0)

        auth_tx2 = MPTokenAuthorize(
            account=WALLET.classic_address,
            mptoken_issuance_id=mpt_issuance_id,
            holder=wallet2.classic_address,
        )

        auth_res2 = await sign_and_reliable_submission_async(
            auth_tx2,
            WALLET,
            client,
        )

        self.assertTrue(auth_res2.is_successful())
        self.assertEqual(auth_res2.result["engine_result"], "tesSUCCESS")

        auth_tx3 = MPTokenAuthorize(
            account=wallet2.classic_address,
            mptoken_issuance_id=mpt_issuance_id,
            flags=MPTokenAuthorizeFlag.TF_MPT_UNAUTHORIZE,
        )

        auth_res3 = await sign_and_reliable_submission_async(
            auth_tx3,
            wallet2,
            client,
        )

        self.assertTrue(auth_res3.is_successful())
        self.assertEqual(auth_res3.result["engine_result"], "tesSUCCESS")

        # confirm MPToken ledger object is removed
        account_objects_response3 = await client.request(
            AccountObjects(account=wallet2.address, type=AccountObjectType.MPTOKEN)
        )

        # Should no longer hold an MPToken ledger object
        self.assertTrue(len(account_objects_response3.result["account_objects"]) == 0)
