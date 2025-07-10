from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    JSON_RPC_CLIENT,
    LEDGER_ACCEPT_REQUEST,
    create_mpt_token_and_authorize_source,
    fund_wallet,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import DESTINATION, WALLET
from xrpl.models import EscrowCreate, EscrowFinish, Ledger, MPTokenIssuanceCreateFlag
from xrpl.models.amounts import MPTAmount
from xrpl.models.requests.account_objects import AccountObjects, AccountObjectType
from xrpl.models.response import ResponseStatus
from xrpl.wallet.main import Wallet

ACCOUNT = WALLET.address

AMOUNT = "10000"
CONDITION = (
    "A0258020E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855810100"
)
DESTINATION_TAG = 23480
SOURCE_TAG = 11747


class TestEscrowCreate(IntegrationTestCase):

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
    async def test_all_fields(self, client):
        ledger = await client.request(Ledger(ledger_index="validated"))
        close_time = ledger.result["ledger"]["close_time"]
        escrow_create = EscrowCreate(
            account=WALLET.classic_address,
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
            await client.request(LEDGER_ACCEPT_REQUEST)
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
