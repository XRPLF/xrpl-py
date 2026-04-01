"""Integration tests for SponsorshipSet transaction type (XLS-68 §9)."""

from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from xrpl.asyncio.transaction import autofill, sign
from xrpl.models import AccountObjects, AccountObjectType, SponsorshipSet
from xrpl.models.requests import SubmitMultisigned
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import SignerEntry, SignerListSet
from xrpl.models.transactions.sponsorship_set import SponsorshipSetFlag
from xrpl.transaction.multisign import multisign
from xrpl.wallet import Wallet


class TestSponsorshipSet(IntegrationTestCase):

    # ── §9.1 CounterpartySponsor field (sponsee-initiated delete) ───────
    # Only the sponsor can create/update; the sponsee
    # may only use CounterpartySponsor with tfDeleteObject.

    @test_async_and_sync(globals())
    async def test_delete_via_counterparty_sponsor(self, client):
        """Sponsee deletes sponsorship using CounterpartySponsor."""
        sponsor_wallet = Wallet.create()
        sponsee_wallet = Wallet.create()
        await fund_wallet_async(sponsor_wallet)
        await fund_wallet_async(sponsee_wallet)

        # Sponsor creates the sponsorship.
        create_tx = SponsorshipSet(
            account=sponsor_wallet.address,
            sponsee=sponsee_wallet.address,
        )
        create_resp = await sign_and_reliable_submission_async(
            create_tx, sponsor_wallet, client
        )
        self.assertEqual(create_resp.result["engine_result"], "tesSUCCESS")

        # Sponsee deletes via CounterpartySponsor + tfDeleteObject.
        delete_tx = SponsorshipSet(
            account=sponsee_wallet.address,
            counterparty_sponsor=sponsor_wallet.address,
            flags=SponsorshipSetFlag.TF_DELETE_OBJECT,
        )
        delete_resp = await sign_and_reliable_submission_async(
            delete_tx, sponsee_wallet, client
        )
        self.assertEqual(delete_resp.status, ResponseStatus.SUCCESS)
        self.assertEqual(delete_resp.result["engine_result"], "tesSUCCESS")

        # Confirm the sponsorship object was deleted.
        account_objects_response = await client.request(
            AccountObjects(
                account=sponsor_wallet.address,
                type=AccountObjectType.SPONSORSHIP,
            )
        )
        self.assertEqual(
            len(account_objects_response.result["account_objects"]),
            0,
        )

    # ── §9.1 all optional fields together ──────────────────────────────

    @test_async_and_sync(globals())
    async def test_sponsorship_set_all_fields(self, client):
        """SponsorshipSet with all optional fields populated."""
        sponsor_wallet = Wallet.create()
        sponsee_wallet = Wallet.create()
        await fund_wallet_async(sponsor_wallet)
        await fund_wallet_async(sponsee_wallet)

        tx = SponsorshipSet(
            account=sponsor_wallet.address,
            sponsee=sponsee_wallet.address,
            fee_amount="2000000",
            max_fee="100000",
            reserve_count=10,
        )
        response = await sign_and_reliable_submission_async(tx, sponsor_wallet, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        account_objects_response = await client.request(
            AccountObjects(
                account=sponsor_wallet.address,
                type=AccountObjectType.SPONSORSHIP,
            )
        )
        objs = account_objects_response.result["account_objects"]
        self.assertTrue(len(objs) > 0)

    # ── Multi-signed sponsor creates sponsorship ─────────────────────

    @test_async_and_sync(
        globals(),
        [
            "xrpl.transaction.autofill",
            "xrpl.transaction.sign",
        ],
    )
    async def test_create_with_multisign_sponsor(self, client):
        """Sponsor with SignerList creates a sponsorship via multisign."""
        sponsor_wallet = Wallet.create()
        sponsee_wallet = Wallet.create()
        signer1 = Wallet.create()
        signer2 = Wallet.create()
        await fund_wallet_async(sponsor_wallet)
        await fund_wallet_async(sponsee_wallet)

        # Set up a SignerList on the sponsor account.
        signer_list_tx = SignerListSet(
            account=sponsor_wallet.address,
            signer_quorum=2,
            signer_entries=[
                SignerEntry(
                    account=signer1.address,
                    signer_weight=1,
                ),
                SignerEntry(
                    account=signer2.address,
                    signer_weight=1,
                ),
            ],
        )
        list_resp = await sign_and_reliable_submission_async(
            signer_list_tx, sponsor_wallet, client
        )
        self.assertEqual(list_resp.result["engine_result"], "tesSUCCESS")

        # Build and autofill the SponsorshipSet.
        tx = SponsorshipSet(
            account=sponsor_wallet.address,
            sponsee=sponsee_wallet.address,
            fee_amount="1000000",
        )
        autofilled_tx = await autofill(tx, client, len([signer1, signer2]))

        # Each signer signs for multisign.
        tx_1 = sign(autofilled_tx, signer1, multisign=True)
        tx_2 = sign(autofilled_tx, signer2, multisign=True)
        multisigned_tx = multisign(autofilled_tx, [tx_1, tx_2])

        response = await client.request(SubmitMultisigned(tx_json=multisigned_tx))
        self.assertTrue(response.is_successful())
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

    # ── §9.2 tfSponsorshipClearRequireSignForFee flag ──────────────────

    @test_async_and_sync(globals())
    async def test_clear_require_sign_for_fee(self, client):
        """Set then clear lsfSponsorshipRequireSignForFee."""
        sponsor_wallet = Wallet.create()
        sponsee_wallet = Wallet.create()
        await fund_wallet_async(sponsor_wallet)
        await fund_wallet_async(sponsee_wallet)

        # Create with the flag set.
        create_tx = SponsorshipSet(
            account=sponsor_wallet.address,
            sponsee=sponsee_wallet.address,
            flags=(SponsorshipSetFlag.TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_FEE),
        )
        create_resp = await sign_and_reliable_submission_async(
            create_tx, sponsor_wallet, client
        )
        self.assertEqual(create_resp.result["engine_result"], "tesSUCCESS")

        # Clear the flag.
        clear_tx = SponsorshipSet(
            account=sponsor_wallet.address,
            sponsee=sponsee_wallet.address,
            flags=(SponsorshipSetFlag.TF_SPONSORSHIP_CLEAR_REQUIRE_SIGN_FOR_FEE),
        )
        clear_resp = await sign_and_reliable_submission_async(
            clear_tx, sponsor_wallet, client
        )
        self.assertEqual(clear_resp.status, ResponseStatus.SUCCESS)
        self.assertEqual(clear_resp.result["engine_result"], "tesSUCCESS")

    # ── §9.2 tfSponsorshipClearRequireSignForReserve flag ──────────────

    @test_async_and_sync(globals())
    async def test_clear_require_sign_for_reserve(self, client):
        """Set then clear lsfSponsorshipRequireSignForReserve."""
        sponsor_wallet = Wallet.create()
        sponsee_wallet = Wallet.create()
        await fund_wallet_async(sponsor_wallet)
        await fund_wallet_async(sponsee_wallet)

        # Create with the flag set.
        create_tx = SponsorshipSet(
            account=sponsor_wallet.address,
            sponsee=sponsee_wallet.address,
            flags=(SponsorshipSetFlag.TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_RESERVE),
        )
        create_resp = await sign_and_reliable_submission_async(
            create_tx, sponsor_wallet, client
        )
        self.assertEqual(create_resp.result["engine_result"], "tesSUCCESS")

        # Clear the flag.
        clear_tx = SponsorshipSet(
            account=sponsor_wallet.address,
            sponsee=sponsee_wallet.address,
            flags=(SponsorshipSetFlag.TF_SPONSORSHIP_CLEAR_REQUIRE_SIGN_FOR_RESERVE),
        )
        clear_resp = await sign_and_reliable_submission_async(
            clear_tx, sponsor_wallet, client
        )
        self.assertEqual(clear_resp.status, ResponseStatus.SUCCESS)
        self.assertEqual(clear_resp.result["engine_result"], "tesSUCCESS")

    # ── §9.2 tfDeleteObject flag ───────────────────────────────────────

    @test_async_and_sync(globals())
    async def test_sponsorship_set_delete(self, client):
        """Create then delete a Sponsorship object."""
        sponsor_wallet = Wallet.create()
        sponsee_wallet = Wallet.create()
        await fund_wallet_async(sponsor_wallet)
        await fund_wallet_async(sponsee_wallet)

        create_tx = SponsorshipSet(
            account=sponsor_wallet.address,
            sponsee=sponsee_wallet.address,
        )
        create_resp = await sign_and_reliable_submission_async(
            create_tx, sponsor_wallet, client
        )
        self.assertEqual(create_resp.status, ResponseStatus.SUCCESS)
        self.assertEqual(create_resp.result["engine_result"], "tesSUCCESS")

        delete_tx = SponsorshipSet(
            account=sponsor_wallet.address,
            sponsee=sponsee_wallet.address,
            flags=SponsorshipSetFlag.TF_DELETE_OBJECT,
        )
        delete_resp = await sign_and_reliable_submission_async(
            delete_tx, sponsor_wallet, client
        )
        self.assertEqual(delete_resp.status, ResponseStatus.SUCCESS)
        self.assertEqual(delete_resp.result["engine_result"], "tesSUCCESS")

        account_objects_response = await client.request(
            AccountObjects(
                account=sponsor_wallet.address,
                type=AccountObjectType.SPONSORSHIP,
            )
        )
        self.assertEqual(len(account_objects_response.result["account_objects"]), 0)
