"""Integration tests for sponsor-signature signing utilities (XLS-0068).

These tests exercise the full co-signing flow described in XLS-0068 §3.2:

  1. Sponsee builds and autofills a transaction with ``sponsor`` /
     ``sponsor_flags`` fields.
  2. Sponsor (or sponsor key holders) co-sign via ``sign_as_sponsor``.
  3. Sponsee signs the resulting transaction with the standard ``sign`` helper.
  4. Transaction is submitted and validated.

Two scenarios are covered:

* **Single-signature sponsor** – the sponsor account uses a single key.
* **Multi-signature sponsor** – the sponsor account requires multiple keys;
  each holder signs independently and the signatures are merged with
  ``combine_sponsor_signers`` before the sponsee signs.

NOTE: These tests assume the *featureSponsor* amendment is enabled on the
rippled server being tested against.  If the amendment is not enabled,
transactions will return ``"temDISABLED"`` instead of ``"tesSUCCESS"``.
"""

from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from xrpl.asyncio.transaction import autofill, submit
from xrpl.asyncio.transaction.main import sign
from xrpl.models import Payment
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import SignerEntry, SignerListSet
from xrpl.transaction import combine_sponsor_signers, sign_as_sponsor
from xrpl.wallet import Wallet

# Sponsor-type flags (XLS-0068).
_TF_SPONSOR_FEE = 0x00000001
_TF_SPONSOR_RESERVE = 0x00000002


class TestSponsorSigner(IntegrationTestCase):
    # -----------------------------------------------------------------------
    # Single-signature sponsor
    # -----------------------------------------------------------------------

    @test_async_and_sync(
        globals(), ["xrpl.transaction.autofill", "xrpl.transaction.submit"]
    )
    async def test_single_sig_sponsor_payment(self, client):
        """Single-key sponsor co-signs a Payment; sponsee signs and submits."""
        sponsor_wallet = Wallet.create()
        sponsee_wallet = Wallet.create()
        destination_wallet = Wallet.create()

        await fund_wallet_async(sponsor_wallet)
        await fund_wallet_async(sponsee_wallet)
        await fund_wallet_async(destination_wallet)

        # Step 1 – Sponsee builds and autofills the transaction.
        payment = Payment(
            account=sponsee_wallet.address,
            destination=destination_wallet.address,
            amount="1000000",
            sponsor=sponsor_wallet.address,
            sponsor_flags=_TF_SPONSOR_FEE,
        )
        autofilled = await autofill(payment, client)

        # Step 2 – Sponsee signs first (sets SigningPubKey + TxnSignature).
        sponsee_signed = sign(autofilled, sponsee_wallet)

        self.assertIsNotNone(sponsee_signed.txn_signature)
        self.assertEqual(sponsee_signed.signing_pub_key, sponsee_wallet.public_key)

        # Step 3 – Sponsor co-signs the already-signed transaction.
        sponsor_result = sign_as_sponsor(sponsor_wallet, sponsee_signed)

        self.assertIsNotNone(sponsor_result.tx.sponsor_signature)
        self.assertEqual(
            sponsor_result.tx.sponsor_signature.signing_pub_key,
            sponsor_wallet.public_key,
        )
        self.assertIsNotNone(sponsor_result.tx.sponsor_signature.txn_signature)
        self.assertIsNone(sponsor_result.tx.sponsor_signature.signers)
        self.assertIsNotNone(sponsor_result.tx_blob)

        # Step 4 – Submit and verify.
        response = await submit(sponsor_result.tx, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

    # -----------------------------------------------------------------------
    # Multi-signature sponsor
    # -----------------------------------------------------------------------

    @test_async_and_sync(
        globals(), ["xrpl.transaction.autofill", "xrpl.transaction.submit"]
    )
    async def test_multisig_sponsor_payment(self, client):
        """Multi-key sponsor signs a Payment; signers merged, sponsee submits."""
        sponsor_wallet = Wallet.create()
        sponsor_key1 = Wallet.create()
        sponsor_key2 = Wallet.create()
        sponsee_wallet = Wallet.create()
        destination_wallet = Wallet.create()

        await fund_wallet_async(sponsor_wallet)
        await fund_wallet_async(sponsee_wallet)
        await fund_wallet_async(destination_wallet)

        # Set up a SignerList on the sponsor account so it can multi-sign.
        signer_list_tx = SignerListSet(
            account=sponsor_wallet.address,
            signer_quorum=2,
            signer_entries=[
                SignerEntry(account=sponsor_key1.address, signer_weight=1),
                SignerEntry(account=sponsor_key2.address, signer_weight=1),
            ],
        )
        await sign_and_reliable_submission_async(signer_list_tx, sponsor_wallet, client)

        # Step 1 – Sponsee builds and autofills the transaction.
        payment = Payment(
            account=sponsee_wallet.address,
            destination=destination_wallet.address,
            amount="1000000",
            sponsor=sponsor_wallet.address,
            sponsor_flags=_TF_SPONSOR_FEE,
        )
        autofilled = await autofill(payment, client)

        # Step 2 – Sponsee signs first (sets SigningPubKey + TxnSignature).
        sponsee_signed = sign(autofilled, sponsee_wallet)
        self.assertIsNotNone(sponsee_signed.txn_signature)

        # Step 3 – Each key holder produces a multisig sponsor contribution.
        sig1_result = sign_as_sponsor(sponsor_key1, sponsee_signed, multisign=True)
        sig2_result = sign_as_sponsor(sponsor_key2, sponsee_signed, multisign=True)

        # Each result must carry exactly one Signer entry.
        self.assertIsNotNone(sig1_result.tx.sponsor_signature)
        self.assertEqual(len(sig1_result.tx.sponsor_signature.signers), 1)
        self.assertEqual(
            sig1_result.tx.sponsor_signature.signers[0].account,
            sponsor_key1.address,
        )

        self.assertIsNotNone(sig2_result.tx.sponsor_signature)
        self.assertEqual(len(sig2_result.tx.sponsor_signature.signers), 1)
        self.assertEqual(
            sig2_result.tx.sponsor_signature.signers[0].account,
            sponsor_key2.address,
        )

        # Step 4 – Merge all sponsor signers into one transaction.
        combined = combine_sponsor_signers([sig1_result.tx, sig2_result.tx])

        self.assertEqual(len(combined.tx.sponsor_signature.signers), 2)
        # Signers must be sorted by canonical account ID bytes (ascending).
        from xrpl.core.addresscodec import decode_classic_address

        ids = [
            decode_classic_address(s.account).hex().upper()
            for s in combined.tx.sponsor_signature.signers
        ]
        self.assertEqual(ids, sorted(ids))

        # Step 5 – Submit and verify.
        response = await submit(combined.tx, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")
