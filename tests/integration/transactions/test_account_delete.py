"""Integration test for sponsored AccountDelete.

When a sponsored account is deleted:
- Destination must equal AccountRoot.Sponsor
- Remaining XRP transfers to the sponsor
- Sponsor's SponsoringAccountCount decrements
"""

from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    LEDGER_ACCEPT_REQUEST,
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from xrpl.asyncio.transaction import autofill, sign, submit
from xrpl.core.binarycodec import encode_for_signing
from xrpl.core.keypairs import sign as keypairs_sign
from xrpl.models import SponsorshipTransfer
from xrpl.models.requests import AccountInfo
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import AccountDelete
from xrpl.models.transactions.sponsorship_transfer import SponsorshipTransferFlag
from xrpl.utils import xrp_to_drops
from xrpl.wallet import Wallet

# Sponsor-type flags (XLS-0068).
_TF_SPONSOR_RESERVE = 0x00000002

# AccountDelete requires a special fee of 5 XRP.
# See https://xrpl.org/accountdelete.html#special-transaction-cost.
ACCOUNT_DELETE_FEE = xrp_to_drops(5)

# AccountDelete requires current_ledger_index >= account_sequence + 256.
_LEDGERS_TO_ADVANCE = 260


def _build_sponsor_signed_tx(transfer_tx, sponsee_wallet, sponsor_wallet):
    """Sign a SponsorshipTransfer as the sponsee, then co-sign."""
    signed_tx = sign(transfer_tx, sponsee_wallet)
    tx_json = signed_tx.to_xrpl()
    sponsor_sig = keypairs_sign(
        bytes.fromhex(encode_for_signing(tx_json)),
        sponsor_wallet.private_key,
    )
    tx_json["SponsorSignature"] = {
        "SigningPubKey": sponsor_wallet.public_key,
        "TxnSignature": sponsor_sig,
    }
    return SponsorshipTransfer.from_xrpl(tx_json)


class TestAccountDeleteSponsored(IntegrationTestCase):

    @test_async_and_sync(
        globals(),
        ["xrpl.transaction.autofill", "xrpl.transaction.submit"],
    )
    async def test_sponsored_account_delete(self, client):
        """Sponsored account deletes itself; destination = sponsor."""
        sponsor_wallet = Wallet.create()
        sponsee_wallet = Wallet.create()
        await fund_wallet_async(sponsor_wallet)
        await fund_wallet_async(sponsee_wallet)

        # Step 1: Create account-level sponsorship (sponsor -> sponsee).
        create_tx = SponsorshipTransfer(
            account=sponsee_wallet.address,
            flags=SponsorshipTransferFlag.TF_SPONSORSHIP_CREATE,
            sponsor_flags=2,
            sponsor=sponsor_wallet.address,
        )
        create_tx = await autofill(create_tx, client)
        final_create_tx = _build_sponsor_signed_tx(
            create_tx, sponsee_wallet, sponsor_wallet
        )
        create_response = await submit(final_create_tx, client)
        await client.request(LEDGER_ACCEPT_REQUEST)
        self.assertEqual(create_response.status, ResponseStatus.SUCCESS)
        self.assertEqual(create_response.result["engine_result"], "tesSUCCESS")

        # Step 2: Advance enough ledgers so the sponsee account
        # satisfies the AccountDelete sequence requirement.
        for _ in range(_LEDGERS_TO_ADVANCE):
            await client.request(LEDGER_ACCEPT_REQUEST)

        # Step 3: Submit AccountDelete from the sponsee.
        # Destination must be the sponsor.
        delete_tx = AccountDelete(
            account=sponsee_wallet.address,
            destination=sponsor_wallet.address,
            fee=ACCOUNT_DELETE_FEE,
        )
        delete_response = await sign_and_reliable_submission_async(
            delete_tx, sponsee_wallet, client, check_fee=False
        )
        self.assertEqual(delete_response.status, ResponseStatus.SUCCESS)
        self.assertEqual(delete_response.result["engine_result"], "tesSUCCESS")

    @test_async_and_sync(
        globals(),
        ["xrpl.transaction.autofill", "xrpl.transaction.submit"],
    )
    async def test_sponsored_account_delete_wrong_destination(self, client):
        """A sponsored account's remaining XRP must go to its sponsor.

        If the AccountRoot carries a `Sponsor`, a `Destination` other
        than that sponsor is rejected with `tecNO_SPONSOR_PERMISSION` -- the
        sponsor funded the account reserve, so it must be repaid.
        """
        sponsor_wallet = Wallet.create()
        sponsee_wallet = Wallet.create()
        other_wallet = Wallet.create()
        await fund_wallet_async(sponsor_wallet)
        await fund_wallet_async(sponsee_wallet)
        await fund_wallet_async(other_wallet)

        # Make the sponsee's account reserve sponsored.
        create_tx = SponsorshipTransfer(
            account=sponsee_wallet.address,
            flags=SponsorshipTransferFlag.TF_SPONSORSHIP_CREATE,
            sponsor=sponsor_wallet.address,
            sponsor_flags=_TF_SPONSOR_RESERVE,
        )
        autofilled = await autofill(create_tx, client)
        create_response = await submit(
            _build_sponsor_signed_tx(autofilled, sponsee_wallet, sponsor_wallet), client
        )
        await client.request(LEDGER_ACCEPT_REQUEST)
        self.assertEqual(create_response.result["engine_result"], "tesSUCCESS")

        for _ in range(_LEDGERS_TO_ADVANCE):
            await client.request(LEDGER_ACCEPT_REQUEST)

        # Destination is a third party, not the sponsor.
        delete_tx = AccountDelete(
            account=sponsee_wallet.address,
            destination=other_wallet.address,
            fee=ACCOUNT_DELETE_FEE,
        )
        delete_response = await sign_and_reliable_submission_async(
            delete_tx, sponsee_wallet, client, check_fee=False
        )
        self.assertEqual(
            delete_response.result["engine_result"], "tecNO_SPONSOR_PERMISSION"
        )

    @test_async_and_sync(
        globals(),
        ["xrpl.transaction.autofill", "xrpl.transaction.submit"],
    )
    async def test_sponsoring_account_cannot_be_deleted(self, client):
        """A sponsor cannot delete itself while it still sponsors anything.

        A non-zero `SponsoringOwnerCount` or `SponsoringAccountCount`
        yields `tecHAS_OBLIGATIONS`. The sponsor must transfer or dissolve its
        sponsorships first -- it cannot walk away from the reserve it committed.
        """
        sponsor_wallet = Wallet.create()
        sponsee_wallet = Wallet.create()
        destination_wallet = Wallet.create()
        await fund_wallet_async(sponsor_wallet)
        await fund_wallet_async(sponsee_wallet)
        await fund_wallet_async(destination_wallet)

        # The sponsor takes on the sponsee's account reserve, which sets
        # SponsoringAccountCount on the sponsor.
        create_tx = SponsorshipTransfer(
            account=sponsee_wallet.address,
            flags=SponsorshipTransferFlag.TF_SPONSORSHIP_CREATE,
            sponsor=sponsor_wallet.address,
            sponsor_flags=_TF_SPONSOR_RESERVE,
        )
        autofilled = await autofill(create_tx, client)
        create_response = await submit(
            _build_sponsor_signed_tx(autofilled, sponsee_wallet, sponsor_wallet), client
        )
        await client.request(LEDGER_ACCEPT_REQUEST)
        self.assertEqual(create_response.result["engine_result"], "tesSUCCESS")

        sponsor_info = await client.request(AccountInfo(account=sponsor_wallet.address))
        self.assertGreater(
            sponsor_info.result["account_data"].get("SponsoringAccountCount", 0), 0
        )

        for _ in range(_LEDGERS_TO_ADVANCE):
            await client.request(LEDGER_ACCEPT_REQUEST)

        delete_tx = AccountDelete(
            account=sponsor_wallet.address,
            destination=destination_wallet.address,
            fee=ACCOUNT_DELETE_FEE,
        )
        delete_response = await sign_and_reliable_submission_async(
            delete_tx, sponsor_wallet, client, check_fee=False
        )
        self.assertEqual(delete_response.result["engine_result"], "tecHAS_OBLIGATIONS")
