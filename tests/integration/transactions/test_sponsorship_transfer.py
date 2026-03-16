"""Integration tests for SponsorshipTransfer transaction type (XLS-68)."""

from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    LEDGER_ACCEPT_REQUEST,
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from xrpl.asyncio.transaction import autofill, sign, submit
from xrpl.core.addresscodec import decode_classic_address
from xrpl.core.binarycodec import encode_for_multisigning, encode_for_signing
from xrpl.core.keypairs import sign as keypairs_sign
from xrpl.models import SponsorshipTransfer
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import SignerEntry, SignerListSet
from xrpl.models.transactions.sponsorship_transfer import SponsorshipTransferFlag
from xrpl.wallet import Wallet


def _build_sponsor_signed_tx(transfer_tx, sponsee_wallet, sponsor_wallet):
    """Sign a SponsorshipTransfer as the sponsee, then co-sign.

    Returns a fully-signed SponsorshipTransfer ready to submit.
    """
    # Sign as the sponsee (primary signer) — sets SigningPubKey
    signed_tx = sign(transfer_tx, sponsee_wallet)

    # Compute the sponsor's co-signature over the signed tx.
    # SigningPubKey (isSigningField=true) is included in the hash;
    # TxnSignature/SponsorSignature (isSigningField=false) excluded.
    tx_json = signed_tx.to_xrpl()
    sponsor_sig = keypairs_sign(
        bytes.fromhex(encode_for_signing(tx_json)),
        sponsor_wallet.private_key,
    )

    # Attach the SponsorSignature
    tx_json["SponsorSignature"] = {
        "SigningPubKey": sponsor_wallet.public_key,
        "TxnSignature": sponsor_sig,
    }
    return SponsorshipTransfer.from_xrpl(tx_json)


class TestSponsorshipTransfer(IntegrationTestCase):

    @test_async_and_sync(
        globals(),
        ["xrpl.transaction.autofill", "xrpl.transaction.submit"],
    )
    async def test_basic_sponsorship_transfer(self, client):
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
        final_create_tx = _build_sponsor_signed_tx(
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
        final_reassign_tx = _build_sponsor_signed_tx(
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
        final_create_tx = _build_sponsor_signed_tx(
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
        create_tx = await autofill(create_tx, client)

        # Sign as the sponsee (primary signer).
        signed_tx = sign(create_tx, sponsee_wallet)
        tx_json = signed_tx.to_xrpl()

        # Each signer signs via encode_for_multisigning.
        signers = []
        for signer_wallet in [signer1, signer2]:
            sig = keypairs_sign(
                bytes.fromhex(encode_for_multisigning(tx_json, signer_wallet.address)),
                signer_wallet.private_key,
            )
            signers.append(
                {
                    "Signer": {
                        "Account": signer_wallet.address,
                        "SigningPubKey": signer_wallet.public_key,
                        "TxnSignature": sig,
                    }
                }
            )

        # Sort signers by decoded account (XRPL requirement).
        signers.sort(key=lambda s: decode_classic_address(s["Signer"]["Account"]))

        # Attach multi-signed SponsorSignature.
        tx_json["SponsorSignature"] = {"Signers": signers}
        final_tx = SponsorshipTransfer.from_xrpl(tx_json)

        create_response = await submit(final_tx, client)
        await client.request(LEDGER_ACCEPT_REQUEST)
        self.assertEqual(create_response.status, ResponseStatus.SUCCESS)
        self.assertEqual(create_response.result["engine_result"], "tesSUCCESS")
