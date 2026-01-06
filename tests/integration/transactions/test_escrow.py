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
    "0061736d010000000108026000017f60000002160103656e760e6765745f6c65646765725f"
    "73716e000003030201000503010002063e0a7f004180080b7f004180080b7f004180100b7f"
    "004180100b7f00418090040b7f004180080b7f00418090040b7f00418080080b7f0041000b"
    "7f0041010b07b0010d066d656d6f72790200115f5f7761736d5f63616c6c5f63746f727300"
    "010666696e69736800020362756603000c5f5f64736f5f68616e646c6503010a5f5f646174"
    "615f656e6403020b5f5f737461636b5f6c6f7703030c5f5f737461636b5f6869676803040d"
    "5f5f676c6f62616c5f6261736503050b5f5f686561705f6261736503060a5f5f686561705f"
    "656e6403070d5f5f6d656d6f72795f6261736503080c5f5f7461626c655f6261736503090a"
    "150202000b1001017f100022004100200041044b1b0b007f0970726f647563657273010c70"
    "726f6365737365642d62790105636c616e675f31392e312e352d776173692d73646b202868"
    "747470733a2f2f6769746875622e636f6d2f6c6c766d2f6c6c766d2d70726f6a6563742061"
    "62346235613264623538323935386166316565333038613739306366646234326264323437"
    "32302900490f7461726765745f6665617475726573042b0f6d757461626c652d676c6f6261"
    "6c732b087369676e2d6578742b0f7265666572656e63652d74797065732b0a6d756c746976"
    "616c7565"
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
