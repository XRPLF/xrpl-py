"""Integration tests for Payment tfSponsorCreatedAccount flag (XLS-68).

When a Payment carries ``TF_SPONSOR_CREATED_ACCOUNT`` and targets a not-yet-funded
destination, the sending account creates the destination account and sponsors its
account reserve. Because the reserve is covered by the sponsor, the delivered
amount can be as little as 1 drop.
"""

from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from xrpl.models import Payment
from xrpl.models.requests import AccountInfo
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions.payment import PaymentFlag
from xrpl.wallet import Wallet


class TestSponsorCreatedAccount(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_sponsor_created_account(self, client):
        """Sponsor creates and funds the reserve of a brand-new account."""
        sponsor_wallet = Wallet.create()
        await fund_wallet_async(sponsor_wallet)

        new_account = Wallet.create()

        payment = Payment(
            account=sponsor_wallet.address,
            destination=new_account.address,
            amount="1",
            flags=PaymentFlag.TF_SPONSOR_CREATED_ACCOUNT,
        )
        response = await sign_and_reliable_submission_async(
            payment, sponsor_wallet, client
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # The destination account now exists on-ledger.
        new_account_info = await client.request(
            AccountInfo(account=new_account.address)
        )
        self.assertTrue(new_account_info.is_successful())

        # The sponsor now sponsors one account reserve.
        sponsor_info = await client.request(AccountInfo(account=sponsor_wallet.address))
        self.assertEqual(
            sponsor_info.result["account_data"].get("SponsoringAccountCount"),
            1,
        )
