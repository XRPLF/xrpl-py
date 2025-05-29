from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    accept_ledger_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import DESTINATION, WALLET
from xrpl.models import EscrowCancel, EscrowCreate, EscrowFinish, Ledger
from xrpl.models.response import ResponseStatus

ACCOUNT = WALLET.address

AMOUNT = "10000"
CONDITION = (
    "A0258020E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855810100"
)
DESTINATION_TAG = 23480
SOURCE_TAG = 11747

FINISH_FUNCTION = (
    "0061736d010000000105016000017f02190108686f73745f6c69620c6765"
    "744c656467657253716e00000302010005030100100611027f00418080c0"
    "000b7f00418080c0000b072e04066d656d6f727902000666696e69736800"
    "010a5f5f646174615f656e6403000b5f5f686561705f6261736503010a09"
    "010700100041044a0b004d0970726f64756365727302086c616e67756167"
    "65010452757374000c70726f6365737365642d6279010572757374631d31"
    "2e38352e31202834656231363132353020323032352d30332d3135290049"
    "0f7461726765745f6665617475726573042b0f6d757461626c652d676c6f"
    "62616c732b087369676e2d6578742b0f7265666572656e63652d74797065"
    "732b0a6d756c746976616c7565"
)


class TestEscrow(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_all_fields_cancel(self, client):
        ledger = await client.request(Ledger(ledger_index="validated"))
        close_time = ledger.result["ledger"]["close_time"]
        escrow_create = EscrowCreate(
            account=ACCOUNT,
            amount=AMOUNT,
            destination=DESTINATION.classic_address,
            destination_tag=DESTINATION_TAG,
            cancel_after=close_time + 3,
            finish_after=close_time + 2,
            source_tag=SOURCE_TAG,
        )
        response = await sign_and_reliable_submission_async(
            escrow_create, WALLET, client
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")
        sequence = response.result["tx_json"]["Sequence"]
        # TODO: check account_objects

        for _ in range(3):
            await accept_ledger_async()

        escrow_cancel = EscrowCancel(
            account=ACCOUNT,
            owner=ACCOUNT,
            offer_sequence=sequence,
        )
        response = await sign_and_reliable_submission_async(
            escrow_cancel, WALLET, client
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

    @test_async_and_sync(globals())
    async def test_all_fields_finish(self, client):
        ledger = await client.request(Ledger(ledger_index="validated"))
        close_time = ledger.result["ledger"]["close_time"]
        escrow_create = EscrowCreate(
            account=ACCOUNT,
            amount=AMOUNT,
            destination=DESTINATION.classic_address,
            destination_tag=DESTINATION_TAG,
            finish_after=close_time + 2,
            source_tag=SOURCE_TAG,
        )
        response = await sign_and_reliable_submission_async(
            escrow_create, WALLET, client
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")
        sequence = response.result["tx_json"]["Sequence"]
        # TODO: check account_objects

        for _ in range(2):
            await accept_ledger_async()

        escrow_finish = EscrowFinish(
            account=ACCOUNT,
            owner=ACCOUNT,
            offer_sequence=sequence,
        )
        response = await sign_and_reliable_submission_async(
            escrow_finish, WALLET, client
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

    @test_async_and_sync(globals())
    async def test_finish_function(self, client):
        ledger = await client.request(Ledger(ledger_index="validated"))
        close_time = ledger.result["ledger"]["close_time"]
        escrow_create = EscrowCreate(
            account=ACCOUNT,
            amount=AMOUNT,
            destination=DESTINATION.classic_address,
            finish_function=FINISH_FUNCTION,
            cancel_after=close_time + 200,
        )
        response = await sign_and_reliable_submission_async(
            escrow_create, WALLET, client
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")
        sequence = response.result["tx_json"]["Sequence"]
        # TODO: check account_objects

        escrow_finish = EscrowFinish(
            account=ACCOUNT,
            owner=ACCOUNT,
            offer_sequence=sequence,
            computation_allowance=5,
        )
        response = await sign_and_reliable_submission_async(
            escrow_finish, WALLET, client
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")
