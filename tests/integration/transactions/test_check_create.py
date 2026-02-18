from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    create_mpt_token_and_authorize_source_async,
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import DESTINATION, WALLET
from xrpl.models.amounts import MPTAmount
from xrpl.models.requests.account_objects import AccountObjects, AccountObjectType
from xrpl.models.requests.ledger_entry import LedgerEntry
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import (
    CheckCreate,
    MPTokenAuthorize,
    MPTokenIssuanceCreate,
    MPTokenIssuanceCreateFlag,
)
from xrpl.wallet import Wallet

ACCOUNT = WALLET.address
DESTINATION_TAG = 1
SENDMAX = "100000000"
EXPIRATION = 970113521
INVOICE_ID = "6F1DFD1D0FE8A32E40E1F2C05CF1C15545BAB56B617F9C6C2D63A6B704BEF59B"


class TestCheckCreate(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_all_fields(self, client):
        check_create = CheckCreate(
            account=ACCOUNT,
            destination=DESTINATION.address,
            destination_tag=DESTINATION_TAG,
            send_max=SENDMAX,
            expiration=EXPIRATION,
            invoice_id=INVOICE_ID,
        )
        response = await sign_and_reliable_submission_async(
            check_create, WALLET, client
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

    @test_async_and_sync(globals())
    async def test_use_MPT_with_Check(self, client):
        issuer = Wallet.create()
        await fund_wallet_async(issuer)
        check_destination_wallet = Wallet.create()
        await fund_wallet_async(check_destination_wallet)

        mpt_issuance_id = await create_mpt_token_and_authorize_source_async(
            issuer=issuer,
            source=check_destination_wallet,
            client=client,
            flags=[
                MPTokenIssuanceCreateFlag.TF_MPT_CAN_TRANSFER,
                MPTokenIssuanceCreateFlag.TF_MPT_CAN_TRADE,
            ],
        )

        send_max = MPTAmount(mpt_issuance_id=mpt_issuance_id, value="50")
        response = await sign_and_reliable_submission_async(
            CheckCreate(
                account=issuer.classic_address,
                destination=check_destination_wallet.classic_address,
                send_max=send_max,
            ),
            issuer,
            client,
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Find the check object ID via account_objects
        account_objects_response = await client.request(
            AccountObjects(
                account=check_destination_wallet.classic_address,
                type=AccountObjectType.CHECK,
            )
        )
        checks = account_objects_response.result["account_objects"]
        self.assertEqual(len(checks), 1)
        check_index = checks[0]["index"]

        # Validate the check using ledger_entry
        ledger_entry_response = await client.request(LedgerEntry(check=check_index))
        check_node = ledger_entry_response.result["node"]
        self.assertEqual(check_node["LedgerEntryType"], "Check")
        self.assertEqual(check_node["Account"], issuer.classic_address)
        self.assertEqual(
            check_node["Destination"], check_destination_wallet.classic_address
        )
        self.assertEqual(
            check_node["SendMax"],
            {"mpt_issuance_id": mpt_issuance_id, "value": "50"},
        )
