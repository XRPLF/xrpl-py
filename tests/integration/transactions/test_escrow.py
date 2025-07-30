from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    JSON_RPC_CLIENT,
    accept_ledger_async,
    create_mpt_token_and_authorize_source,
    fund_wallet,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import DESTINATION, WALLET
from xrpl.models import (
    EscrowCancel,
    EscrowCreate,
    EscrowFinish,
    Ledger,
    MPTokenIssuanceCreateFlag,
)
from xrpl.models.amounts.mpt_amount import MPTAmount
from xrpl.models.requests.account_objects import AccountObjects, AccountObjectType
from xrpl.models.response import ResponseStatus
from xrpl.wallet import Wallet

ACCOUNT = WALLET.address

AMOUNT = "10000"
CONDITION = (
    "A0258020E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855810100"
)
DESTINATION_TAG = 23480
SOURCE_TAG = 11747

FINISH_FUNCTION = (
    "0061736d0100000001150460027f7f017f60037f7f7e017f6000017f60000002300208686f73745f6"
    "c69620e6765745f6c65646765725f73716e000008686f73745f6c69620974726163655f6e756d0001"
    "030302020305030100110619037f01418080c0000b7f00418b80c0000b7f00419080c0000b072e040"
    "66d656d6f727902000666696e69736800020a5f5f646174615f656e6403010b5f5f686561705f6261"
    "736503020a69026301027f23808080800041106b22002480808080002000410036020c02402000410"
    "c6a41081080808080002201417f4a0d00418080c08000410b2001ac1081808080001a108380808000"
    "000b200028020c2101200041106a248080808000200141044b0b0300000b0b140100418080c0000b0"
    "b6572726f725f636f64653d00dd01046e616d6500100f6c65646765725f73716e2e7761736d01a301"
    "0400355f5a4e387872706c5f73746434686f737431346765745f6c65646765725f73716e313768666"
    "5343539333764623461656439366245012f5f5a4e387872706c5f73746434686f7374397472616365"
    "5f6e756d3137686139376531613763346138636231333245020666696e69736803305f5a4e34636f7"
    "2653970616e69636b696e673970616e69635f666d7431376862393162616461636536656538323837"
    "45071201000f5f5f737461636b5f706f696e746572090a0100072e726f64617461004d0970726f647"
    "56365727302086c616e6775616765010452757374000c70726f6365737365642d6279010572757374"
    "631d312e38352e31202834656231363132353020323032352d30332d31352900490f7461726765745"
    "f6665617475726573042b0a6d756c746976616c75652b0f6d757461626c652d676c6f62616c732b0f"
    "7265666572656e63652d74797065732b087369676e2d657874"
)

issuer = Wallet.create()
source = Wallet.create()
destination = Wallet.create()
good_mpt_issuance_id = ""
bad_mpt_issuance_id = ""


class TestEscrow(IntegrationTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        client = JSON_RPC_CLIENT

        # Create issuer, source, and destination wallets.
        cls.issuer = Wallet.create()
        cls.source = Wallet.create()
        cls.destination = Wallet.create()

        fund_wallet(cls.issuer)
        fund_wallet(cls.source)
        fund_wallet(cls.destination)

        cls.good_mpt_issuance_id = create_mpt_token_and_authorize_source(
            cls.issuer,
            cls.source,
            client,
            [
                MPTokenIssuanceCreateFlag.TF_MPT_CAN_ESCROW,
                MPTokenIssuanceCreateFlag.TF_MPT_CAN_TRANSFER,
            ],
        )

        cls.bad_mpt_issuance_id = create_mpt_token_and_authorize_source(
            cls.issuer,
            cls.source,
            client,
        )

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
            await accept_ledger_async(wait=True)

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
            await accept_ledger_async(wait=True)

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
    async def test_mpt_based_escrow(self, client):
        # Create Escrow with MPToken.
        ledger = await client.request(Ledger(ledger_index="validated"))
        close_time = ledger.result["ledger"]["close_time"]

        escrowed_amount = MPTAmount(
            mpt_issuance_id=self.good_mpt_issuance_id,
            value="1",
        )

        finish_after = close_time + 2

        escrow_create = EscrowCreate(
            account=self.source.classic_address,
            amount=escrowed_amount,
            destination=self.destination.classic_address,
            finish_after=finish_after,
            cancel_after=close_time + 1000,
        )
        response = await sign_and_reliable_submission_async(
            escrow_create, self.source, client
        )
        escrow_create_seq = response.result["tx_json"]["Sequence"]

        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Confirm Escrow ledger object was created.
        account_objects_response = await client.request(
            AccountObjects(account=self.source.address, type=AccountObjectType.ESCROW)
        )

        escrow_objects = account_objects_response.result["account_objects"]
        self.assertTrue(
            any(obj["Amount"] == escrowed_amount.to_dict() for obj in escrow_objects),
            "No Escrow object with expected Amount found",
        )

        # Confirm MPToken ledger object was created.
        account_objects_response = await client.request(
            AccountObjects(account=self.source.address, type=AccountObjectType.MPTOKEN)
        )
        mptoken_objects = account_objects_response.result["account_objects"]
        self.assertTrue(
            any(
                obj["MPTokenIssuanceID"] == escrowed_amount.mpt_issuance_id
                and obj["LockedAmount"] == escrowed_amount.value
                for obj in mptoken_objects
            ),
            "No MPTOKEN object with expected MPTokenIssuanceID amd LockedAmount found",
        )

        # Confirm MPTokenIssuance ledger object was created.
        account_objects_response = await client.request(
            AccountObjects(
                account=self.issuer.address, type=AccountObjectType.MPT_ISSUANCE
            )
        )

        mpt_issuance_objects = account_objects_response.result["account_objects"]

        self.assertTrue(
            any(
                obj["mpt_issuance_id"] == escrowed_amount.mpt_issuance_id
                and obj["LockedAmount"] == escrowed_amount.value
                for obj in mpt_issuance_objects
            ),
            "No MPT_ISSUANCE object with expected "
            "mpt_issuance_id and LockedAmount found",
        )

        # Wait for the finish_after time to pass before finishing the escrow.
        close_time = 0
        while close_time <= finish_after:
            await accept_ledger_async(wait=True)
            ledger = await client.request(Ledger(ledger_index="validated"))
            close_time = ledger.result["ledger"]["close_time"]

        # Finish the escrow.
        escrow_finish = EscrowFinish(
            account=self.destination.classic_address,
            owner=self.source.classic_address,
            offer_sequence=escrow_create_seq,
        )
        response = await sign_and_reliable_submission_async(
            escrow_finish, self.destination, client
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Confirm MPToken ledger object was created for destination.
        account_objects_response = await client.request(
            AccountObjects(
                account=self.destination.address, type=AccountObjectType.MPTOKEN
            )
        )

        dest_mptoken_objects = account_objects_response.result["account_objects"]

        self.assertTrue(
            any(
                obj["MPTokenIssuanceID"] == escrowed_amount.mpt_issuance_id
                for obj in dest_mptoken_objects
            ),
            "No destination MPTOKEN object with expected MPTokenIssuanceID found",
        )

    @test_async_and_sync(globals())
    async def test_mpt_based_escrow_failure(self, client):
        # Create Escrow with MPToken.
        ledger = await client.request(Ledger(ledger_index="validated"))
        close_time = ledger.result["ledger"]["close_time"]

        escrowed_amount = MPTAmount(
            mpt_issuance_id=self.bad_mpt_issuance_id,
            value="1",
        )

        finish_after = close_time + 2

        escrow_create = EscrowCreate(
            account=self.source.classic_address,
            amount=escrowed_amount,
            destination=self.destination.classic_address,
            finish_after=finish_after,
            cancel_after=close_time + 1000,
        )

        # Transaction fails with tecNO_PERMISSION because lsfMPTCanEscrow is not set.
        response = await sign_and_reliable_submission_async(
            escrow_create, self.source, client
        )

        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tecNO_PERMISSION")

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
            computation_allowance=20000,
        )
        response = await sign_and_reliable_submission_async(
            escrow_finish, WALLET, client
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")
