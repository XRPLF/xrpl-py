"""Integration tests for SponsorshipTransfer transaction type."""

from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    LEDGER_ACCEPT_REQUEST,
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from xrpl.asyncio.transaction import autofill, sign, submit
from xrpl.models import (
    AccountObjects,
    AccountObjectType,
    DepositPreauth,
    SponsorshipTransfer,
)
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import SignerEntry, SignerListSet
from xrpl.models.transactions.sponsorship_transfer import SponsorshipTransferFlag
from xrpl.transaction import combine_sponsor_signers, sign_as_sponsor
from xrpl.wallet import Wallet


def _sponsee_then_sponsor(transfer_tx, sponsee_wallet, sponsor_wallet):
    """Sign as the sponsee, then have the sponsor co-sign.

    Thin wrapper over the public API so each call site stays one line; the
    signing itself is `sign_as_sponsor`, not a reimplementation of it.
    """
    return sign_as_sponsor(sponsor_wallet, sign(transfer_tx, sponsee_wallet)).tx


class TestSponsorshipTransfer(IntegrationTestCase):

    @test_async_and_sync(
        globals(),
        ["xrpl.transaction.autofill", "xrpl.transaction.submit"],
    )
    async def test_basic_sponsorship_transfer(self, client):
        """Account-level sponsorship: CREATE, then REASSIGN to a new sponsor.

        With no `object_id` the target is the sponsee's own account reserve, so
        this covers the account-level path that `test_object_level_...` does not.
        """
        sponsor_wallet = Wallet.create()
        sponsee_wallet = Wallet.create()
        new_sponsor_wallet = Wallet.create()
        await fund_wallet_async(sponsor_wallet)
        await fund_wallet_async(sponsee_wallet)
        await fund_wallet_async(new_sponsor_wallet)

        # Step 1: Create account-level sponsorship.
        # No object_id means this is an account sponsor,
        # not an object sponsor.
        create_tx = SponsorshipTransfer(
            account=sponsee_wallet.address,
            flags=SponsorshipTransferFlag.TF_SPONSORSHIP_CREATE,
            sponsor_flags=2,
            sponsor=sponsor_wallet.address,
        )
        create_tx = await autofill(create_tx, client)
        final_create_tx = _sponsee_then_sponsor(
            create_tx, sponsee_wallet, sponsor_wallet
        )
        create_response = await submit(final_create_tx, client)
        await client.request(LEDGER_ACCEPT_REQUEST)
        self.assertEqual(create_response.status, ResponseStatus.SUCCESS)
        self.assertEqual(create_response.result["engine_result"], "tesSUCCESS")

        # Step 2: Reassign the account sponsorship.
        reassign_tx = SponsorshipTransfer(
            account=sponsee_wallet.address,
            flags=(SponsorshipTransferFlag.TF_SPONSORSHIP_REASSIGN),
            sponsor_flags=2,
            sponsor=new_sponsor_wallet.address,
        )
        reassign_tx = await autofill(reassign_tx, client)
        final_reassign_tx = _sponsee_then_sponsor(
            reassign_tx, sponsee_wallet, new_sponsor_wallet
        )
        reassign_response = await submit(final_reassign_tx, client)
        await client.request(LEDGER_ACCEPT_REQUEST)
        self.assertEqual(reassign_response.status, ResponseStatus.SUCCESS)
        self.assertEqual(
            reassign_response.result["engine_result"],
            "tesSUCCESS",
        )

    @test_async_and_sync(
        globals(),
        ["xrpl.transaction.autofill", "xrpl.transaction.submit"],
    )
    async def test_sponsored_to_unsponsored(self, client):
        """Sponsored -> Unsponsored: sponsee ends sponsorship."""
        sponsor_wallet = Wallet.create()
        sponsee_wallet = Wallet.create()
        await fund_wallet_async(sponsor_wallet)
        await fund_wallet_async(sponsee_wallet)

        # Create account-level sponsorship (sponsor -> sponsee).
        create_tx = SponsorshipTransfer(
            account=sponsee_wallet.address,
            flags=SponsorshipTransferFlag.TF_SPONSORSHIP_CREATE,
            sponsor_flags=2,
            sponsor=sponsor_wallet.address,
        )
        create_tx = await autofill(create_tx, client)
        final_create_tx = _sponsee_then_sponsor(
            create_tx, sponsee_wallet, sponsor_wallet
        )
        create_response = await submit(final_create_tx, client)
        await client.request(LEDGER_ACCEPT_REQUEST)
        self.assertEqual(create_response.status, ResponseStatus.SUCCESS)
        self.assertEqual(create_response.result["engine_result"], "tesSUCCESS")

        # End the sponsorship. The sponsee submits with
        # tfSponsorshipEnd. No sponsor, sponsor_flags, or
        # sponsor_signature needed.
        end_tx = SponsorshipTransfer(
            account=sponsee_wallet.address,
            flags=SponsorshipTransferFlag.TF_SPONSORSHIP_END,
        )
        end_response = await sign_and_reliable_submission_async(
            end_tx, sponsee_wallet, client
        )
        self.assertEqual(end_response.status, ResponseStatus.SUCCESS)
        self.assertEqual(end_response.result["engine_result"], "tesSUCCESS")

    @test_async_and_sync(
        globals(),
        ["xrpl.transaction.autofill", "xrpl.transaction.submit"],
    )
    async def test_create_with_multisign_sponsor(self, client):
        """Create sponsorship where the sponsor uses a SignerList."""
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
        list_response = await sign_and_reliable_submission_async(
            signer_list_tx, sponsor_wallet, client
        )
        self.assertEqual(list_response.result["engine_result"], "tesSUCCESS")

        # Build and autofill the SponsorshipTransfer.
        create_tx = SponsorshipTransfer(
            account=sponsee_wallet.address,
            flags=SponsorshipTransferFlag.TF_SPONSORSHIP_CREATE,
            sponsor_flags=2,
            sponsor=sponsor_wallet.address,
        )
        # Two sponsor signers are attached below, and `Fee` is a signing field --
        # final before those signatures exist -- so the count must be declared.
        # base * (1 + |tx.Signers| + |SponsorSignature.Signers|) = base * 3.
        create_tx = await autofill(create_tx, client, sponsor_signers_count=2)

        # Sign as the sponsee (primary signer), then each sponsor key holder
        # contributes independently and the contributions are merged.
        signed_tx = sign(create_tx, sponsee_wallet)
        final_tx = combine_sponsor_signers(
            [
                sign_as_sponsor(signer1, signed_tx, multisign=True).tx,
                sign_as_sponsor(signer2, signed_tx, multisign=True).tx,
            ]
        ).tx
        self.assertEqual(len(final_tx.sponsor_signature.signers), 2)

        create_response = await submit(final_tx, client)
        await client.request(LEDGER_ACCEPT_REQUEST)
        self.assertEqual(create_response.status, ResponseStatus.SUCCESS)
        self.assertEqual(create_response.result["engine_result"], "tesSUCCESS")

    @test_async_and_sync(
        globals(),
        ["xrpl.transaction.autofill", "xrpl.transaction.submit"],
    )
    async def test_object_level_sponsorship_transfer(self, client):
        """Object-level transfer (sfObjectID): CREATE -> REASSIGN -> END.

        Exercises the ``object_id`` field of SponsorshipTransfer against a
        concrete owned ledger object (a DepositPreauth owned by the sponsee).
        """
        sponsor_wallet = Wallet.create()
        new_sponsor_wallet = Wallet.create()
        sponsee_wallet = Wallet.create()
        authorized_wallet = Wallet.create()
        await fund_wallet_async(sponsor_wallet)
        await fund_wallet_async(new_sponsor_wallet)
        await fund_wallet_async(sponsee_wallet)
        await fund_wallet_async(authorized_wallet)

        # The sponsee creates an owned object (DepositPreauth).
        deposit_preauth = DepositPreauth(
            account=sponsee_wallet.address,
            authorize=authorized_wallet.address,
        )
        dp_response = await sign_and_reliable_submission_async(
            deposit_preauth, sponsee_wallet, client
        )
        self.assertEqual(dp_response.result["engine_result"], "tesSUCCESS")

        # Look up the ledger index (object_id) of the created object.
        objects_response = await client.request(
            AccountObjects(
                account=sponsee_wallet.address,
                type=AccountObjectType.DEPOSIT_PREAUTH,
            )
        )
        account_objects = objects_response.result["account_objects"]
        self.assertEqual(len(account_objects), 1)
        object_id = account_objects[0]["index"]

        # Step 1: CREATE object-level reserve sponsorship (sponsor co-signs).
        create_tx = SponsorshipTransfer(
            account=sponsee_wallet.address,
            object_id=object_id,
            flags=SponsorshipTransferFlag.TF_SPONSORSHIP_CREATE,
            sponsor_flags=2,
            sponsor=sponsor_wallet.address,
        )
        create_tx = await autofill(create_tx, client)
        final_create_tx = _sponsee_then_sponsor(
            create_tx, sponsee_wallet, sponsor_wallet
        )
        create_response = await submit(final_create_tx, client)
        await client.request(LEDGER_ACCEPT_REQUEST)
        self.assertEqual(create_response.status, ResponseStatus.SUCCESS)
        self.assertEqual(create_response.result["engine_result"], "tesSUCCESS")

        # Step 2: REASSIGN the object sponsorship to a new sponsor.
        reassign_tx = SponsorshipTransfer(
            account=sponsee_wallet.address,
            object_id=object_id,
            flags=SponsorshipTransferFlag.TF_SPONSORSHIP_REASSIGN,
            sponsor_flags=2,
            sponsor=new_sponsor_wallet.address,
        )
        reassign_tx = await autofill(reassign_tx, client)
        final_reassign_tx = _sponsee_then_sponsor(
            reassign_tx, sponsee_wallet, new_sponsor_wallet
        )
        reassign_response = await submit(final_reassign_tx, client)
        await client.request(LEDGER_ACCEPT_REQUEST)
        self.assertEqual(reassign_response.status, ResponseStatus.SUCCESS)
        self.assertEqual(reassign_response.result["engine_result"], "tesSUCCESS")

        # Step 3: END the object sponsorship (sponsee owns it, no co-sign).
        end_tx = SponsorshipTransfer(
            account=sponsee_wallet.address,
            object_id=object_id,
            flags=SponsorshipTransferFlag.TF_SPONSORSHIP_END,
        )
        end_response = await sign_and_reliable_submission_async(
            end_tx, sponsee_wallet, client
        )
        self.assertEqual(end_response.status, ResponseStatus.SUCCESS)
        self.assertEqual(end_response.result["engine_result"], "tesSUCCESS")
