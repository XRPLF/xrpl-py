"""Integration tests for sponsor-signature signing utilities (XLS-0068).

These tests exercise the full co-signing flow:

  1. Sponsee builds and autofills a transaction with ``sponsor`` /
     ``sponsor_flags`` fields.
  2. Sponsor (or sponsor key holders) co-sign via ``sign_as_sponsor``.
  3. Sponsee signs the resulting transaction with the standard ``sign`` helper.
  4. Transaction is submitted and validated.

Two scenarios are covered:

* **Single-signature sponsor** - the sponsor account uses a single key.
* **Multi-signature sponsor** - the sponsor account requires multiple keys;
  each holder signs independently and the signatures are merged with
  ``combine_sponsor_signers`` before the sponsee signs.

NOTE: These tests assume the *featureSponsor* amendment is enabled on the
rippled server being tested against.  If the amendment is not enabled,
transactions will return ``"temDISABLED"`` instead of ``"tesSUCCESS"``.
"""

from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    LEDGER_ACCEPT_REQUEST,
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from xrpl.asyncio.transaction import autofill, submit
from xrpl.asyncio.transaction.main import sign
from xrpl.models import AccountObjects, AccountObjectType, CheckCreate, Payment
from xrpl.models.requests import AccountInfo
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import SignerEntry, SignerListSet
from xrpl.transaction import combine_sponsor_signers, sign_as_sponsor
from xrpl.transaction.multisign import multisign
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

        # Step 1 - Sponsee builds and autofills the transaction.
        payment = Payment(
            account=sponsee_wallet.address,
            destination=destination_wallet.address,
            amount="1000000",
            sponsor=sponsor_wallet.address,
            sponsor_flags=_TF_SPONSOR_FEE,
        )
        autofilled = await autofill(payment, client)

        # Step 2 - Sponsee signs first (sets SigningPubKey + TxnSignature).
        sponsee_signed = sign(autofilled, sponsee_wallet)

        self.assertIsNotNone(sponsee_signed.txn_signature)
        self.assertEqual(sponsee_signed.signing_pub_key, sponsee_wallet.public_key)

        # Step 3 - Sponsor co-signs the already-signed transaction.
        sponsor_result = sign_as_sponsor(sponsor_wallet, sponsee_signed)

        self.assertIsNotNone(sponsor_result.tx.sponsor_signature)
        self.assertEqual(
            sponsor_result.tx.sponsor_signature.signing_pub_key,
            sponsor_wallet.public_key,
        )
        self.assertIsNotNone(sponsor_result.tx.sponsor_signature.txn_signature)
        self.assertIsNone(sponsor_result.tx.sponsor_signature.signers)
        self.assertIsNotNone(sponsor_result.tx_blob)

        # Step 4 - Submit and verify.
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
        list_response = await sign_and_reliable_submission_async(
            signer_list_tx, sponsor_wallet, client
        )
        self.assertEqual(list_response.result["engine_result"], "tesSUCCESS")

        # Step 1 - Sponsee builds and autofills the transaction.
        #
        # `sponsor_signers_count` is required here: `Fee` is a signing field, so
        # it is final before the sponsor signs, which means SponsorSignature does
        # not exist yet and the count cannot be read off the transaction. Without
        # it the fee is one base fee and the ledger returns telINSUF_FEE_P.
        payment = Payment(
            account=sponsee_wallet.address,
            destination=destination_wallet.address,
            amount="1000000",
            sponsor=sponsor_wallet.address,
            sponsor_flags=_TF_SPONSOR_FEE,
        )
        autofilled = await autofill(payment, client, sponsor_signers_count=2)

        # Step 2 - Sponsee signs first (sets SigningPubKey + TxnSignature).
        sponsee_signed = sign(autofilled, sponsee_wallet)
        self.assertIsNotNone(sponsee_signed.txn_signature)

        # Step 3 - Each key holder produces a multisig sponsor contribution.
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

        # Step 4 - Merge all sponsor signers into one transaction.
        combined = combine_sponsor_signers([sig1_result.tx, sig2_result.tx])

        self.assertEqual(len(combined.tx.sponsor_signature.signers), 2)
        # Signers must be sorted by canonical account ID bytes (ascending).
        from xrpl.core.addresscodec import decode_classic_address

        ids = [
            decode_classic_address(s.account).hex().upper()
            for s in combined.tx.sponsor_signature.signers
        ]
        self.assertEqual(ids, sorted(ids))

        # Step 5 - Submit and verify.
        response = await submit(combined.tx, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

    # -----------------------------------------------------------------------
    # Reserve sponsorship (spfSponsorReserve) at object creation
    # -----------------------------------------------------------------------

    @test_async_and_sync(
        globals(), ["xrpl.transaction.autofill", "xrpl.transaction.submit"]
    )
    async def test_reserve_sponsor_check_create(self, client):
        """Sponsor covers the object reserve of a sponsee's newly-created Check.

        Exercises the common ``sfSponsor`` + ``spfSponsorReserve`` path on an
        object-creating transaction (CheckCreate is allow-listed for reserve
        sponsorship in rippled), co-signed via ``sign_as_sponsor``.
        """
        sponsor_wallet = Wallet.create()
        sponsee_wallet = Wallet.create()
        destination_wallet = Wallet.create()

        await fund_wallet_async(sponsor_wallet)
        await fund_wallet_async(sponsee_wallet)
        await fund_wallet_async(destination_wallet)

        # Sponsee builds a CheckCreate whose reserve is covered by the sponsor.
        check = CheckCreate(
            account=sponsee_wallet.address,
            destination=destination_wallet.address,
            send_max="1000000",
            sponsor=sponsor_wallet.address,
            sponsor_flags=_TF_SPONSOR_RESERVE,
        )
        autofilled = await autofill(check, client)

        # Sponsee signs first, then the sponsor co-signs.
        sponsee_signed = sign(autofilled, sponsee_wallet)
        sponsor_result = sign_as_sponsor(sponsor_wallet, sponsee_signed)

        response = await submit(sponsor_result.tx, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")
        await client.request(LEDGER_ACCEPT_REQUEST)

        # The created Check records the sponsor that covers its reserve.
        objects_response = await client.request(
            AccountObjects(
                account=sponsee_wallet.address,
                type=AccountObjectType.CHECK,
            )
        )
        checks = objects_response.result["account_objects"]
        self.assertEqual(len(checks), 1)
        self.assertEqual(checks[0].get("Sponsor"), sponsor_wallet.address)

        # The sponsee still *owns* the Check, so its OwnerCount
        # increments as normal -- and SponsoredOwnerCount increments alongside it,
        # as a subset (rippled asserts OwnerCount >= SponsoredOwnerCount). The
        # reserve is computed as
        #     OwnerCount - SponsoredOwnerCount + SponsoringOwnerCount
        # so the two cancel for the sponsee (net 0) while the sponsor's
        # SponsoringOwnerCount adds 1. The burden moves; the ownership does not.
        sponsee_info = await client.request(AccountInfo(account=sponsee_wallet.address))
        sponsee_data = sponsee_info.result["account_data"]
        self.assertEqual(sponsee_data.get("SponsoredOwnerCount"), 1)
        self.assertEqual(sponsee_data.get("OwnerCount"), 1)

        sponsor_info = await client.request(AccountInfo(account=sponsor_wallet.address))
        self.assertEqual(
            sponsor_info.result["account_data"].get("SponsoringOwnerCount"), 1
        )

    # -----------------------------------------------------------------------
    # Multi-signature sponsee
    #
    # A multi-signing sponsee never populates SigningPubKey -- an empty value is
    # how the ledger signals multi-signing, and the signatures live in Signers
    # instead. `sign_as_sponsor(..., sponsee_multisign=True)` confirms the empty
    # value is deliberate.
    # -----------------------------------------------------------------------

    @test_async_and_sync(
        globals(), ["xrpl.transaction.autofill", "xrpl.transaction.submit"]
    )
    async def test_multisig_sponsee_single_sig_sponsor(self, client):
        """Multi-key sponsee, single-key sponsor."""
        sponsor_wallet = Wallet.create()
        sponsee_wallet = Wallet.create()
        sponsee_key1 = Wallet.create()
        sponsee_key2 = Wallet.create()
        destination_wallet = Wallet.create()

        await fund_wallet_async(sponsor_wallet)
        await fund_wallet_async(sponsee_wallet)
        await fund_wallet_async(destination_wallet)

        # Give the sponsee a SignerList so it can multi-sign.
        signer_list_tx = SignerListSet(
            account=sponsee_wallet.address,
            signer_quorum=2,
            signer_entries=[
                SignerEntry(account=sponsee_key1.address, signer_weight=1),
                SignerEntry(account=sponsee_key2.address, signer_weight=1),
            ],
        )
        list_response = await sign_and_reliable_submission_async(
            signer_list_tx, sponsee_wallet, client
        )
        self.assertEqual(list_response.result["engine_result"], "tesSUCCESS")

        # `signers_count` covers the sponsee's two signatures; the sponsor
        # single-signs and is not billed.
        payment = Payment(
            account=sponsee_wallet.address,
            destination=destination_wallet.address,
            amount="1000000",
            sponsor=sponsor_wallet.address,
            sponsor_flags=_TF_SPONSOR_FEE,
        )
        autofilled = await autofill(payment, client, signers_count=2)

        # The sponsee multi-signs: SigningPubKey stays empty.
        part1 = sign(autofilled, sponsee_key1, multisign=True)
        part2 = sign(autofilled, sponsee_key2, multisign=True)
        sponsee_signed = multisign(autofilled, [part1, part2])
        self.assertEqual(sponsee_signed.signing_pub_key, "")
        self.assertEqual(len(sponsee_signed.signers), 2)

        # The sponsor co-signs the empty-SigningPubKey transaction.
        sponsor_result = sign_as_sponsor(
            sponsor_wallet, sponsee_signed, sponsee_multisign=True
        )
        self.assertIsNotNone(sponsor_result.tx.sponsor_signature.signing_pub_key)
        self.assertEqual(len(sponsor_result.tx.signers), 2)

        response = await submit(sponsor_result.tx, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

    @test_async_and_sync(
        globals(), ["xrpl.transaction.autofill", "xrpl.transaction.submit"]
    )
    async def test_multisig_sponsee_multisig_sponsor(self, client):
        """Both parties multi-sign; the two signer sets are independent."""
        sponsor_wallet = Wallet.create()
        sponsor_key1 = Wallet.create()
        sponsor_key2 = Wallet.create()
        sponsee_wallet = Wallet.create()
        sponsee_key1 = Wallet.create()
        sponsee_key2 = Wallet.create()
        destination_wallet = Wallet.create()

        await fund_wallet_async(sponsor_wallet)
        await fund_wallet_async(sponsee_wallet)
        await fund_wallet_async(destination_wallet)

        for wallet, keys in (
            (sponsee_wallet, (sponsee_key1, sponsee_key2)),
            (sponsor_wallet, (sponsor_key1, sponsor_key2)),
        ):
            list_response = await sign_and_reliable_submission_async(
                SignerListSet(
                    account=wallet.address,
                    signer_quorum=2,
                    signer_entries=[
                        SignerEntry(account=key.address, signer_weight=1)
                        for key in keys
                    ],
                ),
                wallet,
                client,
            )
            self.assertEqual(list_response.result["engine_result"], "tesSUCCESS")

        # base * (1 + |tx.Signers| + |SponsorSignature.Signers|) = base * 5
        payment = Payment(
            account=sponsee_wallet.address,
            destination=destination_wallet.address,
            amount="1000000",
            sponsor=sponsor_wallet.address,
            sponsor_flags=_TF_SPONSOR_FEE,
        )
        autofilled = await autofill(
            payment, client, signers_count=2, sponsor_signers_count=2
        )

        sponsee_signed = multisign(
            autofilled,
            [
                sign(autofilled, sponsee_key1, multisign=True),
                sign(autofilled, sponsee_key2, multisign=True),
            ],
        )
        self.assertEqual(sponsee_signed.signing_pub_key, "")

        # Each sponsor key holder signs independently, then the contributions
        # merge into SponsorSignature.Signers.
        combined = combine_sponsor_signers(
            [
                sign_as_sponsor(
                    sponsor_key1,
                    sponsee_signed,
                    multisign=True,
                    sponsee_multisign=True,
                ).tx,
                sign_as_sponsor(
                    sponsor_key2,
                    sponsee_signed,
                    multisign=True,
                    sponsee_multisign=True,
                ).tx,
            ]
        )
        self.assertEqual(len(combined.tx.signers), 2)
        self.assertEqual(len(combined.tx.sponsor_signature.signers), 2)

        response = await submit(combined.tx, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")
