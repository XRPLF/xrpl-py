"""Integration tests for LedgerEntry request with Sponsorship (XLS-68)."""

from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from xrpl.models import SponsorshipSet
from xrpl.models.requests.ledger_entry import LedgerEntry, Sponsorship
from xrpl.models.response import ResponseStatus
from xrpl.wallet import Wallet


class TestLedgerEntrySponsorship(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_ledger_entry_sponsorship_by_owner_and_sponsee(self, client):
        """Query a Sponsorship ledger entry by owner + sponsee."""
        sponsor_wallet = Wallet.create()
        sponsee_wallet = Wallet.create()
        await fund_wallet_async(sponsor_wallet)
        await fund_wallet_async(sponsee_wallet)

        # Create a sponsorship object.
        tx = SponsorshipSet(
            account=sponsor_wallet.address,
            sponsee=sponsee_wallet.address,
        )
        response = await sign_and_reliable_submission_async(tx, sponsor_wallet, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Query via LedgerEntry with Sponsorship(owner, sponsee).
        ledger_response = await client.request(
            LedgerEntry(
                sponsorship=Sponsorship(
                    sponsor=sponsor_wallet.address,
                    sponsee=sponsee_wallet.address,
                )
            )
        )
        self.assertTrue(
            ledger_response.is_successful(),
            f"LedgerEntry failed: {ledger_response.result}",
        )
        node = ledger_response.result["node"]
        self.assertEqual(node["LedgerEntryType"], "Sponsorship")
        self.assertEqual(node["Owner"], sponsor_wallet.address)
        self.assertEqual(node["Sponsee"], sponsee_wallet.address)
