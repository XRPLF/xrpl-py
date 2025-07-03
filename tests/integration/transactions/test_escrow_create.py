from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    LEDGER_ACCEPT_REQUEST,
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import DESTINATION, WALLET
from xrpl.models import (
    EscrowCreate,
    EscrowFinish,
    Ledger,
    MPTokenAuthorize,
    MPTokenIssuanceCreate,
    MPTokenIssuanceCreateFlag,
    Payment,
)
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
        # Create issuer, source, and destination wallets.
        issuer = Wallet.create()
        await fund_wallet_async(issuer)

        source = Wallet.create()
        await fund_wallet_async(source)

        destination = Wallet.create()
        await fund_wallet_async(destination)

        # Create MPToken that can be used in Escrow.
        mp_token_issuance_tx = MPTokenIssuanceCreate(
            account=issuer.classic_address,
            flags=[
                MPTokenIssuanceCreateFlag.TF_MPT_CAN_ESCROW,
                MPTokenIssuanceCreateFlag.TF_MPT_CAN_TRANSFER,
            ],
        )

        await sign_and_reliable_submission_async(mp_token_issuance_tx, issuer, client)

        # confirm MPTokenIssuance ledger object was created
        account_objects_response = await client.request(
            AccountObjects(account=issuer.address, type=AccountObjectType.MPT_ISSUANCE)
        )

        self.assertEqual(len(account_objects_response.result["account_objects"]), 1)
        mpt_issuance_id = account_objects_response.result["account_objects"][0][
            "mpt_issuance_id"
        ]

        # Source account authorizes itself to hold MPToken.
        mp_token_authorize_tx = MPTokenAuthorize(
            account=source.classic_address,
            mptoken_issuance_id=mpt_issuance_id,
        )

        await sign_and_reliable_submission_async(mp_token_authorize_tx, source, client)

        # Send some MPToken to the source wallet that can be further used in Escrow.
        payment_tx = Payment(
            account=issuer.address,
            destination=source.address,
            amount=MPTAmount(
                mpt_issuance_id=mpt_issuance_id,
                value="1000",
            ),
        )

        await sign_and_reliable_submission_async(payment_tx, issuer, client)

        # Create Escrow with MPToken.
        ledger = await client.request(Ledger(ledger_index="validated"))
        close_time = ledger.result["ledger"]["close_time"]

        escrowed_amount = MPTAmount(
            mpt_issuance_id=mpt_issuance_id,
            value="10",
        )

        finish_after = close_time + 2

        escrow_create = EscrowCreate(
            account=source.classic_address,
            amount=escrowed_amount,
            destination=destination.classic_address,
            finish_after=finish_after,
            cancel_after=close_time + 1000,
        )
        response = await sign_and_reliable_submission_async(
            escrow_create, source, client
        )
        escrow_create_seq = response.result["tx_json"]["Sequence"]

        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Confirm EscrowCreate ledger object was created.
        account_objects_response = await client.request(
            AccountObjects(account=source.address, type=AccountObjectType.ESCROW)
        )

        self.assertEqual(len(account_objects_response.result["account_objects"]), 1)
        self.assertEqual(
            account_objects_response.result["account_objects"][0]["Amount"],
            escrowed_amount.to_dict(),
        )

        # Confirm MPToken ledger object was created.
        account_objects_response = await client.request(
            AccountObjects(account=source.address, type=AccountObjectType.MPTOKEN)
        )

        self.assertEqual(len(account_objects_response.result["account_objects"]), 1)
        self.assertEqual(
            account_objects_response.result["account_objects"][0]["LockedAmount"],
            escrowed_amount.value,
        )
        self.assertEqual(
            account_objects_response.result["account_objects"][0]["MPTokenIssuanceID"],
            escrowed_amount.mpt_issuance_id,
        )

        # Confirm MPTokenIssuance ledger object was created.
        account_objects_response = await client.request(
            AccountObjects(account=issuer.address, type=AccountObjectType.MPT_ISSUANCE)
        )

        self.assertEqual(len(account_objects_response.result["account_objects"]), 1)
        self.assertEqual(
            account_objects_response.result["account_objects"][0]["LockedAmount"],
            escrowed_amount.value,
        )

        # Wait for the finish_after time to pass before finishing the escrow.
        close_time = 0
        while close_time <= finish_after:
            await client.request(LEDGER_ACCEPT_REQUEST)
            ledger = await client.request(Ledger(ledger_index="validated"))
            close_time = ledger.result["ledger"]["close_time"]

        # Finish the escrow.
        escrow_finish = EscrowFinish(
            account=destination.classic_address,
            owner=source.classic_address,
            offer_sequence=escrow_create_seq,
        )
        response = await sign_and_reliable_submission_async(
            escrow_finish, destination, client
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Confirm MPToken ledger object was created for destination.
        account_objects_response = await client.request(
            AccountObjects(account=destination.address, type=AccountObjectType.MPTOKEN)
        )

        self.assertEqual(len(account_objects_response.result["account_objects"]), 1)
        self.assertEqual(
            account_objects_response.result["account_objects"][0]["MPTAmount"],
            escrowed_amount.value,
        )
        self.assertEqual(
            account_objects_response.result["account_objects"][0]["MPTokenIssuanceID"],
            escrowed_amount.mpt_issuance_id,
        )

    @test_async_and_sync(globals())
    async def test_mpt_based_escrow_failure(self, client):
        # Create issuer, source, and destination wallets.
        issuer = Wallet.create()
        await fund_wallet_async(issuer)

        source = Wallet.create()
        await fund_wallet_async(source)

        destination = Wallet.create()
        await fund_wallet_async(destination)

        # Create MPToken that can be used in Escrow.
        mp_token_issuance_tx = MPTokenIssuanceCreate(
            account=issuer.classic_address,
        )

        await sign_and_reliable_submission_async(mp_token_issuance_tx, issuer, client)

        # confirm MPTokenIssuance ledger object was created
        account_objects_response = await client.request(
            AccountObjects(account=issuer.address, type=AccountObjectType.MPT_ISSUANCE)
        )

        self.assertEqual(len(account_objects_response.result["account_objects"]), 1)
        mpt_issuance_id = account_objects_response.result["account_objects"][0][
            "mpt_issuance_id"
        ]

        # Source account authorizes itself to hold MPToken.
        mp_token_authorize_tx = MPTokenAuthorize(
            account=source.classic_address,
            mptoken_issuance_id=mpt_issuance_id,
        )

        await sign_and_reliable_submission_async(mp_token_authorize_tx, source, client)

        # Send some MPToken to the source wallet that can be further used in Escrow.
        payment_tx = Payment(
            account=issuer.address,
            destination=source.address,
            amount=MPTAmount(
                mpt_issuance_id=mpt_issuance_id,
                value="1000",
            ),
        )

        await sign_and_reliable_submission_async(payment_tx, issuer, client)

        # Create Escrow with MPToken.
        ledger = await client.request(Ledger(ledger_index="validated"))
        close_time = ledger.result["ledger"]["close_time"]

        escrowed_amount = MPTAmount(
            mpt_issuance_id=mpt_issuance_id,
            value="10",
        )

        finish_after = close_time + 2

        escrow_create = EscrowCreate(
            account=source.classic_address,
            amount=escrowed_amount,
            destination=destination.classic_address,
            finish_after=finish_after,
            cancel_after=close_time + 1000,
        )

        # Transaction fails with tecNO_PERMISSION because lsfMPTCanEscrow is not set.
        response = await sign_and_reliable_submission_async(
            escrow_create, source, client
        )

        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tecNO_PERMISSION")
