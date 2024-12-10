from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import WALLET
from xrpl.models.requests import Tx
from xrpl.models.requests.account_objects import AccountObjects, AccountObjectType
from xrpl.models.transactions import (
    MPTokenIssuanceCreate,
    MPTokenIssuanceCreateFlag,
    MPTokenIssuanceSet,
    MPTokenIssuanceSetFlag,
)


class TestMPTokenIssuanceSet(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        tx = MPTokenIssuanceCreate(
            account=WALLET.classic_address,
            flags=MPTokenIssuanceCreateFlag.TF_MPT_CAN_LOCK,
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

        set_tx = MPTokenIssuanceSet(
            account=WALLET.classic_address,
            mptoken_issuance_id=mpt_issuance_id,
            flags=MPTokenIssuanceSetFlag.TF_MPT_LOCK,
        )

        set_res = await sign_and_reliable_submission_async(
            set_tx,
            WALLET,
            client,
        )

        self.assertTrue(set_res.is_successful())
        self.assertEqual(set_res.result["engine_result"], "tesSUCCESS")
