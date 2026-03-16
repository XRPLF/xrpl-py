from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import WALLET
from xrpl.models import SponsorshipSet
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import AccountSet
from xrpl.models.transactions.account_set import AccountSetAsfFlag
from xrpl.wallet import Wallet

ACCOUNT = WALLET.address

CLEAR_FLAG = 3
DOMAIN = "6578616D706C652E636F6D".lower()
EMAIL_HASH = "10000000002000000000300000000012"
MESSAGE_KEY = "03AB40A0490F9B7ED8DF29D246BF2D6269820A0EE7742ACDD457BEA7C7D0931EDB"
SET_FLAG = 8
TRANSFER_RATE = 0
TICK_SIZE = 10


class TestAccountSet(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_required_fields_and_set_flag(self, client):
        account_set = AccountSet(
            account=ACCOUNT,
            set_flag=SET_FLAG,
        )
        response = await sign_and_reliable_submission_async(account_set, WALLET, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

    @test_async_and_sync(globals())
    async def test_all_fields_minus_set_flag(self, client):
        account_set = AccountSet(
            account=ACCOUNT,
            clear_flag=CLEAR_FLAG,
            domain=DOMAIN,
            email_hash=EMAIL_HASH,
            message_key=MESSAGE_KEY,
            transfer_rate=TRANSFER_RATE,
            tick_size=TICK_SIZE,
        )
        response = await sign_and_reliable_submission_async(account_set, WALLET, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

    @test_async_and_sync(globals())
    async def test_set_disallow_incoming_sponsor(self, client):
        """Setting ASF_DISALLOW_INCOMING_SPONSOR blocks new sponsorships."""
        sponsee_wallet = Wallet.create()
        sponsor_wallet = Wallet.create()
        await fund_wallet_async(sponsee_wallet)
        await fund_wallet_async(sponsor_wallet)

        # Set the flag on the sponsee account.
        set_tx = AccountSet(
            account=sponsee_wallet.address,
            set_flag=AccountSetAsfFlag.ASF_DISALLOW_INCOMING_SPONSOR,
        )
        set_resp = await sign_and_reliable_submission_async(
            set_tx, sponsee_wallet, client
        )
        self.assertEqual(set_resp.result["engine_result"], "tesSUCCESS")

        # Attempt to create a sponsorship targeting the sponsee.
        sponsor_tx = SponsorshipSet(
            account=sponsor_wallet.address,
            sponsee=sponsee_wallet.address,
        )
        sponsor_resp = await sign_and_reliable_submission_async(
            sponsor_tx, sponsor_wallet, client
        )
        self.assertEqual(sponsor_resp.result["engine_result"], "tecNO_PERMISSION")

    @test_async_and_sync(globals())
    async def test_clear_disallow_incoming_sponsor(self, client):
        """Clearing ASF_DISALLOW_INCOMING_SPONSOR allows sponsorships."""
        sponsee_wallet = Wallet.create()
        sponsor_wallet = Wallet.create()
        await fund_wallet_async(sponsee_wallet)
        await fund_wallet_async(sponsor_wallet)

        # Set then clear the flag.
        set_tx = AccountSet(
            account=sponsee_wallet.address,
            set_flag=AccountSetAsfFlag.ASF_DISALLOW_INCOMING_SPONSOR,
        )
        await sign_and_reliable_submission_async(set_tx, sponsee_wallet, client)

        clear_tx = AccountSet(
            account=sponsee_wallet.address,
            clear_flag=AccountSetAsfFlag.ASF_DISALLOW_INCOMING_SPONSOR,
        )
        clear_resp = await sign_and_reliable_submission_async(
            clear_tx, sponsee_wallet, client
        )
        self.assertEqual(clear_resp.result["engine_result"], "tesSUCCESS")

        # Now creating a sponsorship should succeed.
        sponsor_tx = SponsorshipSet(
            account=sponsor_wallet.address,
            sponsee=sponsee_wallet.address,
        )
        sponsor_resp = await sign_and_reliable_submission_async(
            sponsor_tx, sponsor_wallet, client
        )
        self.assertEqual(sponsor_resp.result["engine_result"], "tesSUCCESS")
