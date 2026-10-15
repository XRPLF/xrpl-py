"""Integration tests for the LedgerEntry request."""

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


class TestLedgerEntry(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_ledger_entry_sponsorship_by_owner_and_sponsee(self, client):
        """Query a Sponsorship ledger entry by owner + sponsee.

        The create passes a `fee_amount_delta` because a `SponsorshipSet` that
        creates the object must leave it with a positive budget, or rippled
        rejects it with `tecNO_PERMISSION`.
        """
        sponsor_wallet = Wallet.create()
        sponsee_wallet = Wallet.create()
        await fund_wallet_async(sponsor_wallet)
        await fund_wallet_async(sponsee_wallet)

        tx = SponsorshipSet(
            account=sponsor_wallet.address,
            sponsee=sponsee_wallet.address,
            fee_amount_delta="1000000",
        )
        response = await sign_and_reliable_submission_async(tx, sponsor_wallet, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

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
        # sfSponseeNode is a required field on the Sponsorship object
        # (the directory node pointer on the sponsee's owner directory).
        self.assertIn("SponseeNode", node)
