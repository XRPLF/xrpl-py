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
    "0061736d010000000105016000017f021b0108686f73745f6c69620e6765745f6c"
    "65646765725f73716e0000030201000405017001010105030100100619037f0141"
    "8080c0000b7f00418080c0000b7f00418080c0000b072d04066d656d6f72790200"
    "05726561647900010a5f5f646174615f656e6403010b5f5f686561705f62617365"
    "03020a0d010b0010808080800041044a0b006e046e616d65000e0d7761736d5f6c"
    "69622e7761736d01430200395f5a4e387761736d5f6c696238686f73745f6c6962"
    "31346765745f6c65646765725f73716e3137686663383539386237646539633036"
    "64624501057265616479071201000f5f5f737461636b5f706f696e746572005509"
    "70726f64756365727302086c616e6775616765010452757374000c70726f636573"
    "7365642d62790105727573746325312e38332e302d6e696768746c792028633266"
    "37346333663920323032342d30392d30392900490f7461726765745f6665617475"
    "726573042b0a6d756c746976616c75652b0f6d757461626c652d676c6f62616c73"
    "2b0f7265666572656e63652d74797065732b087369676e2d657874"
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

        for _ in range(4):
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

        for _ in range(6):
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
        )
        response = await sign_and_reliable_submission_async(
            escrow_finish, WALLET, client
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")
