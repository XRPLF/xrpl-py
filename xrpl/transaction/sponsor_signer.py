"""Helper functions for co-signing transactions as a fee/reserve sponsor.

The sponsored-fee/reserve model lets a *sponsor* account
cover the transaction fee and/or object reserve costs on behalf of a *sponsee*.
When ``lsfSponsorshipRequireSignForFee`` / ``lsfSponsorshipRequireSignForReserve``
is set, or when there is no pre-funded ``Sponsorship`` ledger object, the sponsor
must co-sign each transaction before it is submitted.

Signing flow:

1. The sponsee constructs and autofills the transaction, setting the ``sponsor``
   and ``sponsor_flags`` fields and their own ``signing_pub_key``. They do not
   sign yet.
2. The sponsor calls :func:`sign_as_sponsor` and returns the resulting
   ``SponsorSignature`` to the sponsee.
3. The sponsee signs the transaction and submits it.

Both parties sign the same canonical signing data (``HashPrefix::txSign`` +
the transaction's signing fields).  The sponsor's signature and public key live
inside the ``SponsorSignature`` inner object, while the sponsee's live at the
top level.

Only ``SigningPubKey`` must be settled before the sponsor signs, because it is a
signing field -- filling it in afterwards would change the data the sponsor
signed and silently invalidate their signature.  Neither ``TxnSignature`` nor
``SponsorSignature`` is a signing field, so the two parties' signatures are
independent: the sponsee may equally sign first, in which case
``signing_pub_key`` is already set and steps 2 and 3 swap.

A **multi-signing sponsee** never populates ``SigningPubKey`` at all -- an empty
value is how the ledger signals multi-signing, and the signatures live in
``Signers`` instead.  Pass ``sponsee_multisign=True`` in that case, to confirm
the empty value is deliberate rather than an unset field.

For sponsor accounts that require multiple keys (multi-sig), each key holder
calls :func:`sign_as_sponsor` with ``multisign=True``, then all contributions
are merged with :func:`combine_sponsor_signers`.  The sponsor's and sponsee's
signing modes are independent; either, both, or neither may multi-sign.

This module mirrors the API of :mod:`xrpl.transaction.batch_signers` and
:mod:`xrpl.transaction.counterparty_signer` for consistency.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Union

from xrpl.constants import XRPLException
from xrpl.core.addresscodec import (
    decode_classic_address,
    is_valid_xaddress,
    xaddress_to_classic_address,
)
from xrpl.core.binarycodec import encode, encode_for_multisigning, encode_for_signing
from xrpl.core.keypairs import sign as keypairs_sign
from xrpl.models.transactions import SponsorSignature, Transaction
from xrpl.models.transactions.transaction import Signer
from xrpl.wallet import Wallet


@dataclass
class SignSponsorResult:
    """Result of signing a transaction as the fee/reserve sponsor."""

    tx: Transaction
    """The transaction object with ``sponsor_signature`` populated."""

    tx_blob: str
    """Serialized hex blob of the transaction."""


@dataclass
class CombineSponsorSignersResult:
    """Result of merging multiple sponsor multi-signatures into one transaction."""

    tx: Transaction
    """The transaction object with all sponsor signers merged."""

    tx_blob: str
    """Serialized hex blob ready to be signed by the sponsee and submitted."""


def sign_as_sponsor(
    wallet: Wallet,
    transaction: Union[Transaction, str],
    multisign: Union[bool, str] = False,
    sponsee_multisign: bool = False,
) -> SignSponsorResult:
    """
    Sign a transaction as the fee/reserve sponsor.

    The sponsor's cryptographic approval is placed in the ``SponsorSignature``
    field of the transaction.  The sponsor signs the **same** canonical
    transaction data that the sponsee will sign (``HashPrefix::txSign`` +
    signing-field serialisation), so the sponsee's ``SigningPubKey`` must
    already be settled when the sponsor signs -- either populated with the
    sponsee's key, or deliberately empty because the sponsee multi-signs.

    Args:
        wallet: The sponsor's wallet used for signing.
        transaction: The autofilled transaction to co-sign.  Can be either a
            :class:`~xrpl.models.transactions.Transaction` object or a
            hex-encoded transaction blob.
        multisign: Pass ``True`` (or a classic/x-address string for regular-key
            usage) to produce a multi-signature entry inside
            ``SponsorSignature.Signers``.  Defaults to ``False`` (single-sig).
            This describes how the **sponsor** signs.
        sponsee_multisign: Pass ``True`` when the **sponsee** multi-signs, which
            leaves their ``SigningPubKey`` permanently empty -- that empty value
            is how the ledger signals multi-signing, and the sponsee's signatures
            live in ``Signers`` instead. Without this, an empty
            ``signing_pub_key`` is rejected, since it is otherwise
            indistinguishable from a field the sponsee has not set yet, which
            would invalidate the sponsor's signature once they did.
            Independent of ``multisign``.

    Returns:
        A :class:`SignSponsorResult` containing:

        - ``tx`` - the transaction with ``sponsor_signature`` added.
        - ``tx_blob`` - the serialized transaction blob (no sponsee sig yet).

    Raises:
        XRPLException: If the transaction has no ``sponsor`` field, if
            ``fee`` has not been autofilled yet, if a non-multisig
            ``sponsor_signature`` already exists when ``multisign=False``,
            or if ``signing_pub_key`` is empty and ``sponsee_multisign`` is
            not set
    """
    if isinstance(transaction, str):
        tx = Transaction.from_blob(transaction)
    else:
        tx = transaction

    if tx.sponsor is None:
        raise XRPLException(
            "Transaction must have a `sponsor` field set before the sponsor signs. "
            "Set `sponsor` (and `sponsor_flags`) on the transaction and autofill it "
            "first."
        )

    if tx.fee is None:
        raise XRPLException(
            "Transaction `fee` must be autofilled before the sponsor signs, "
            "because the sponsor is approving the exact fee amount."
        )

    if not multisign and tx.sponsor_signature is not None:
        raise XRPLException(
            "Transaction already has a `sponsor_signature`. To collect several "
            "sponsor signatures, have each key holder call this function with "
            "`multisign=True` on the *same* transaction, then merge the results "
            "with `combine_sponsor_signers`. Calling it again on an "
            "already-signed transaction would replace the existing signature, "
            "not add to it."
        )

    # The sponsor signs the same canonical data as the sponsee, and that data
    # includes SigningPubKey (a signing field). An empty value is ambiguous: it
    # is the ledger's marker for a multi-signing sponsee, but it is also what an
    # unset field looks like -- and if the sponsee populates it afterwards, the
    # sponsor's signature is silently invalidated. Only the caller can tell the
    # two apart.
    if not tx.signing_pub_key and not sponsee_multisign:
        raise XRPLException(
            "Transaction `signing_pub_key` cannot be empty during the Sponsor "
            "signature step. Set the sponsee's `signing_pub_key` first, or pass "
            "`sponsee_multisign=True` if the sponsee multi-signs and the empty "
            "value is intentional."
        )
    tx_json = tx.to_xrpl()

    # Resolve multisign address (if any).
    multisign_address: Optional[str] = None
    if isinstance(multisign, str):
        multisign_address = multisign
    elif multisign:
        multisign_address = wallet.address

    if multisign_address:
        classic_address = (
            xaddress_to_classic_address(multisign_address)[0]
            if is_valid_xaddress(multisign_address)
            else multisign_address
        )
        signature = keypairs_sign(
            bytes.fromhex(encode_for_multisigning(tx_json, classic_address)),
            wallet.private_key,
        )
        sponsor_sig = SponsorSignature(
            signers=[
                Signer(
                    account=classic_address,
                    signing_pub_key=wallet.public_key,
                    txn_signature=signature,
                )
            ]
        )
    else:
        signature = keypairs_sign(
            bytes.fromhex(encode_for_signing(tx_json)),
            wallet.private_key,
        )
        sponsor_sig = SponsorSignature(
            signing_pub_key=wallet.public_key,
            txn_signature=signature,
        )

    tx_dict = tx.to_dict()
    tx_dict["sponsor_signature"] = sponsor_sig
    signed_tx = Transaction.from_dict(tx_dict)
    serialized = encode(signed_tx.to_xrpl())

    return SignSponsorResult(
        tx=signed_tx,
        tx_blob=serialized,
    )


def combine_sponsor_signers(
    transactions: List[Union[Transaction, str]],
) -> CombineSponsorSignersResult:
    """
    Merge multiple sponsor multi-signatures into a single transaction.

    When the sponsor account requires multiple keys, each key holder calls
    :func:`sign_as_sponsor` with ``multisign=True``.  Pass all the resulting
    transactions here to produce one transaction whose
    ``SponsorSignature.Signers`` array contains every contribution.  The
    combined transaction is then handed to the sponsee, who adds their own
    signature before submitting.

    Args:
        transactions: A list of transactions (objects or hex blobs), each
            containing a ``SponsorSignature`` with a non-empty ``Signers``
            array produced by :func:`sign_as_sponsor` with ``multisign=True``.

    Returns:
        A :class:`CombineSponsorSignersResult` containing:

        - ``tx`` - the combined transaction object.
        - ``tx_blob`` - the serialized hex blob ready for the sponsee to sign
          and submit.

    Raises:
        XRPLException: If ``transactions`` is empty, any transaction lacks
            ``SponsorSignature.Signers``, the same sponsor account appears more
            than once, or the transactions differ in fields other than
            ``SponsorSignature.Signers``.
    """
    if len(transactions) == 0:
        raise XRPLException("There are 0 transactions to combine.")

    decoded: List[Transaction] = []
    for tx_or_blob in transactions:
        tx = (
            Transaction.from_blob(tx_or_blob)
            if isinstance(tx_or_blob, str)
            else tx_or_blob
        )
        if (
            tx.sponsor_signature is None
            or tx.sponsor_signature.signers is None
            or len(tx.sponsor_signature.signers) == 0
        ):
            raise XRPLException(
                "All transactions must have a `SponsorSignature` with a non-empty "
                "`Signers` array. Use multisign=True when calling sign_as_sponsor."
            )
        decoded.append(tx)

    _validate_sponsor_transaction_equivalence(decoded)
    combined = _get_transaction_with_all_sponsor_signers(decoded)

    return CombineSponsorSignersResult(
        tx=combined,
        tx_blob=encode(combined.to_xrpl()),
    )


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _validate_sponsor_transaction_equivalence(transactions: List[Transaction]) -> None:
    """Raise if any transaction differs from the first, ignoring Signers."""
    if len(transactions) <= 1:
        return

    def _strip_signers(tx: Transaction) -> Dict[str, object]:
        d = tx.to_xrpl()
        if "SponsorSignature" in d:
            d["SponsorSignature"] = {**d["SponsorSignature"], "Signers": None}
        return d

    example = _strip_signers(transactions[0])
    for tx in transactions[1:]:
        if _strip_signers(tx) != example:
            raise XRPLException(
                "All transactions must be identical except for "
                "SponsorSignature.Signers."
            )


def _get_transaction_with_all_sponsor_signers(
    transactions: List[Transaction],
) -> Transaction:
    """Collect and sort all Signers from every transaction's SponsorSignature."""
    all_signers: List[Signer] = []
    for tx in transactions:
        if (
            tx.sponsor_signature is not None
            and tx.sponsor_signature.signers is not None
        ):
            all_signers.extend(tx.sponsor_signature.signers)

    # rippled rejects a Signers array that repeats an account, so
    # catch a double-passed contribution here rather than at submission.
    accounts = [signer.account for signer in all_signers]
    duplicates = sorted(
        {account for account in accounts if accounts.count(account) > 1}
    )
    if duplicates:
        raise XRPLException(
            f"Duplicate sponsor signer(s) for account(s): {', '.join(duplicates)}. "
            "Each sponsor account may contribute only one signature."
        )

    # XRPL requires signers sorted by account ID (ascending).
    all_signers.sort(key=lambda s: decode_classic_address(s.account).hex().upper())

    tx_dict = transactions[0].to_dict()
    tx_dict["sponsor_signature"] = SponsorSignature(signers=all_signers)
    return Transaction.from_dict(tx_dict)
