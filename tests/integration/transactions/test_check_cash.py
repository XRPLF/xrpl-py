from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    create_mpt_token_and_authorize_source_async,
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import WALLET
from xrpl.models.amounts import MPTAmount
from xrpl.models.requests.account_objects import AccountObjects, AccountObjectType
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import CheckCash, CheckCreate, MPTokenIssuanceCreateFlag
from xrpl.wallet import Wallet

ACCOUNT = WALLET.address
CHECK_ID = "838766BA2B995C00744175F69A1B11E32C3DBC40E64801A4056FCBD657F57334"
AMOUNT = "100000000"
DELIVER_MIN = "100000000"


class TestCheckCash(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_required_fields_with_amount(self, client):
        check_cash = CheckCash(
            account=ACCOUNT,
            check_id=CHECK_ID,
            amount=AMOUNT,
        )
        response = await sign_and_reliable_submission_async(check_cash, WALLET, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        # Getting `tecNO_ENTRY` codes because using a non-existent check ID
        self.assertEqual(response.result["engine_result"], "tecNO_ENTRY")

    @test_async_and_sync(globals())
    async def test_required_fields_with_deliver_min(self, client):
        check_cash = CheckCash(
            account=ACCOUNT,
            check_id=CHECK_ID,
            deliver_min=DELIVER_MIN,
        )
        response = await sign_and_reliable_submission_async(check_cash, WALLET, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tecNO_ENTRY")

    @test_async_and_sync(globals())
    async def test_check_cash_with_mpt(self, client):
        issuer = Wallet.create()
        await fund_wallet_async(issuer)
        destination_check_wallet = Wallet.create()
        await fund_wallet_async(destination_check_wallet)

        mpt_issuance_id = await create_mpt_token_and_authorize_source_async(
            issuer=issuer,
            source=destination_check_wallet,
            client=client,
            flags=[
                MPTokenIssuanceCreateFlag.TF_MPT_CAN_TRANSFER,
                MPTokenIssuanceCreateFlag.TF_MPT_CAN_TRADE,
            ],
        )

        # Issuer creates a check to destination for 50 MPT
        mpt_amount = MPTAmount(mpt_issuance_id=mpt_issuance_id, value="50")
        create_response = await sign_and_reliable_submission_async(
            CheckCreate(
                account=issuer.classic_address,
                destination=destination_check_wallet.classic_address,
                send_max=mpt_amount,
            ),
            issuer,
            client,
        )
        self.assertEqual(create_response.result["engine_result"], "tesSUCCESS")

        # Find the check ID
        account_objects_response = await client.request(
            AccountObjects(
                account=destination_check_wallet.classic_address,
                type=AccountObjectType.CHECK,
            )
        )
        checks = account_objects_response.result["account_objects"]
        self.assertEqual(len(checks), 1)
        mpt_check_id = checks[0]["index"]

        # Destination cashes the check
        cash_response = await sign_and_reliable_submission_async(
            CheckCash(
                account=destination_check_wallet.classic_address,
                check_id=mpt_check_id,
                amount=mpt_amount,
            ),
            destination_check_wallet,
            client,
        )
        self.assertEqual(cash_response.result["engine_result"], "tesSUCCESS")

        # Verify the check was consumed
        account_objects_response = await client.request(
            AccountObjects(
                account=destination_check_wallet.classic_address,
                type=AccountObjectType.CHECK,
            )
        )
        self.assertEqual(len(account_objects_response.result["account_objects"]), 0)
