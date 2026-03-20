"""Helper functions for co-signing transactions as a fee/reserve sponsor (XLS-0068).

XLS-0068 introduces a sponsored-fee/reserve model where a *sponsor* account can
cover the transaction fee and/or object reserve costs on behalf of a *sponsee*.
When ``lsfSponsorshipRequireSignForFee`` / ``lsfSponsorshipRequireSignForReserve``
is set, or when there is no pre-funded ``Sponsorship`` ledger object, the sponsor
must co-sign each transaction before it is submitted.

Signing flow (per rippled implementation):

1. The sponsee constructs and autofills the transaction, setting the ``sponsor``
   and ``sponsor_flags`` fields.
2. The sponsee signs the transaction with the standard ``xrpl.transaction.sign``
   helper (this sets ``SigningPubKey``).
3. The sponsor calls :func:`sign_as_sponsor` on the signed transaction to add
   their ``SponsorSignature``.
4. The sponsee submits the fully-signed transaction.

Both the sponsor and the sponsee sign the same canonical signing data
(``HashPrefix::txSign`` + transaction fields).  The sponsor's signature and
public key live inside the ``SponsorSignature`` inner object, while the
sponsee's live at the top level.

For sponsor accounts that require multiple keys (multi-sig), each key holder
calls :func:`sign_as_sponsor` with ``multisign=True``, then all contributions
are merged with :func:`combine_sponsor_signers`` before the sponsee signs.

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
from xrpl.models.transactions import Transaction
from xrpl.models.transactions.sponsor_signature import SponsorSignature
from xrpl.models.transactions.transaction import Signer
from xrpl.wallet import Wallet


@dataclass
class SignSponsorResult:
    """Result of signing a transaction as the fee/reserve sponsor."""

    tx: Transaction
    """The transaction object with ``sponsor_signature`` populated."""

    tx_blob: str
    """Serialised hex blob of the transaction."""


@dataclass
class CombineSponsorSignersResult:
    """Result of merging multiple sponsor multi-signatures into one transaction."""

    tx: Transaction
    """The transaction object with all sponsor signers merged."""

    tx_blob: str
    """Serialised hex blob ready to be signed by the sponsee and submitted."""


def sign_as_sponsor(
    wallet: Wallet,
    transaction: Union[Transaction, str],
    multisign: Union[bool, str] = False,
) -> SignSponsorResult:
    """
    Sign a transaction as the fee/reserve sponsor (XLS-0068).

    The sponsor's cryptographic approval is placed in the ``SponsorSignature``
    field of the transaction.  The sponsor signs the **same** canonical
    transaction data that the sponsee will sign (``HashPrefix::txSign`` +
    signing-field serialisation), so the sponsee's ``SigningPubKey`` must
    already be present on the transaction when the sponsor signs.


    Args:
        wallet: The sponsor's wallet used for signing.
        transaction: The autofilled transaction to co-sign.  Can be either a
            :class:`~xrpl.models.transactions.Transaction` object or a
            hex-encoded transaction blob.
        multisign: Pass ``True`` (or a classic/x-address string for regular-key
            usage) to produce a multi-signature entry inside
            ``SponsorSignature.Signers``.  Defaults to ``False`` (single-sig).

    Returns:
        A :class:`SignSponsorResult` containing:

        - ``tx`` – the transaction with ``sponsor_signature`` added.
        - ``tx_blob`` – the serialised transaction blob (no sponsee sig yet).

    Raises:
        XRPLException: If the transaction has no ``sponsor`` field, if
            ``fee`` has not been autofilled yet, if a non-multisig
            ``sponsor_signature`` already exists when ``multisign=False``,
            or if ``signing_pub_key`` is empty
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
            "Transaction already has a `sponsor_signature`. "
            "Use multisign=True to add additional signatures to "
            "`SponsorSignature.Signers`."
        )

    # The sponsor signs the same canonical data as the sponsee.  That data
    # includes SigningPubKey (a signing field)
    if not tx.signing_pub_key:
        raise XRPLException(
            "Transaction `signing_pub_key` cannot be empty "
            "during Sponsor signature step."
        )
    tx_dict = tx.to_dict()
    tx = Transaction.from_dict(tx_dict)

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

        - ``tx`` – the combined transaction object.
        - ``tx_blob`` – the serialised hex blob ready for the sponsee to sign
          and submit.

    Raises:
        XRPLException: If ``transactions`` is empty, any transaction lacks
            ``SponsorSignature.Signers``, or the transactions differ in fields
            other than ``SponsorSignature.Signers``.
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

    # XRPL requires signers sorted by account ID (ascending).
    all_signers.sort(key=lambda s: decode_classic_address(s.account).hex().upper())

    tx_dict = transactions[0].to_dict()
    tx_dict["sponsor_signature"] = SponsorSignature(signers=all_signers)
    return Transaction.from_dict(tx_dict)
