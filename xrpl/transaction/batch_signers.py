"""Helper functions for signing multi-account Batch transactions."""

from typing import Dict, List, Optional, Tuple, Union, cast

from xrpl.constants import XRPLException
from xrpl.core.addresscodec.codec import decode_classic_address
from xrpl.core.binarycodec import encode, encode_for_signing_batch
from xrpl.core.binarycodec.main import BatchSigningDict
from xrpl.core.keypairs import sign
from xrpl.models.transactions import Batch, Signer, Transaction
from xrpl.models.transactions.batch import BatchSigner
from xrpl.wallet import Wallet


def _get_batch_seq_value(transaction: Batch) -> int:
    """
    Resolve the sequence value bound into a Batch signature: the ``Sequence`` when
    non-zero, otherwise the ``TicketSequence`` value (or 0).

    Args:
        transaction: The Batch transaction being signed.

    Returns:
        The sequence value to bind into the signature.
    """
    sequence = transaction.sequence or 0
    if sequence != 0:
        return sequence
    return transaction.ticket_sequence or 0


def sign_multiaccount_batch(
    wallet: Wallet,
    transaction: Batch,
    multisign: Union[bool, str] = False,
    batch_account: Optional[str] = None,
) -> Batch:
    """
    Sign a multi-account Batch transaction.

    Args:
        wallet: Wallet instance.
        transaction: The Batch transaction to sign.
        multisign: Specify ``True`` to multi-sign with ``wallet``'s address, or pass
            an address string to multi-sign on behalf of that account (e.g. when
            signing with a regular key). Defaults to ``False`` (single-sign).
        batch_account: The account included in the Batch on whose behalf this
            signature is provided. Defaults to ``wallet``'s address. Use this when the
            signing key differs from the account it signs for (e.g. a regular key).

    Raises:
        XRPLException: If the account signing the transaction doesn't submit (or is
            the counterparty of) an inner transaction in the Batch.

    Returns:
        The Batch transaction with the BatchSigner included.
    """
    signing_account = batch_account if batch_account is not None else wallet.address

    multisign_address: Optional[str] = None
    if isinstance(multisign, str):
        multisign_address = multisign
    elif multisign:
        multisign_address = wallet.address

    # A multi-signed signer must differ from the account it signs for; an account
    # cannot be on its own signer list (rippled: "Invalid multisigner").
    if multisign_address == signing_account:
        raise XRPLException(
            "A multi-signed BatchSigner's signer account must differ from the "
            "batch account."
        )

    # An involved account authorizes an inner transaction (its delegate when
    # present, else its account), is the counterparty of one, or sponsors one.
    involved_accounts = set()
    for tx in transaction.raw_transactions:
        involved_accounts.add(tx.delegate or tx.account)
        counterparty = getattr(tx, "counterparty", None)
        if isinstance(counterparty, str):
            involved_accounts.add(counterparty)

        # The empty SponsorSignature placeholder selects the co-signed path, where
        # the sponsor authorizes through BatchSigners. Without it the sponsorship
        # is pre-funded and the sponsor must stay out, or rippled counts it as an
        # extra signer (temBAD_SIGNER).
        if tx.sponsor is not None and tx.sponsor_signature is not None:
            involved_accounts.add(tx.sponsor)
    if signing_account not in involved_accounts:
        raise XRPLException("Must be signing for an address included in the Batch.")

    fields_to_sign: BatchSigningDict = {
        "account": transaction.account,
        "sequence": _get_batch_seq_value(transaction),
        "flags": transaction._flags_to_int() or 0,
        "transaction_ids": [tx.get_hash() for tx in transaction.raw_transactions],
        "batch_account": signing_account,
    }
    if multisign_address:
        # Multi-signed batch signers also bind the inner signer account.
        fields_to_sign["signer_account"] = multisign_address

    signature = sign(encode_for_signing_batch(fields_to_sign), wallet.private_key)

    if multisign_address:
        signer = Signer(
            account=multisign_address,
            signing_pub_key=wallet.public_key,
            txn_signature=signature,
        )
        batch_signer = BatchSigner(account=signing_account, signers=[signer])
    else:
        batch_signer = BatchSigner(
            account=signing_account,
            signing_pub_key=wallet.public_key,
            txn_signature=signature,
        )

    transaction_dict = transaction.to_dict()
    transaction_dict["batch_signers"] = [batch_signer]

    return Batch.from_dict(transaction_dict)


def combine_batch_signers(transactions: List[Union[Batch, str]]) -> str:
    """
    Takes several transactions with BatchSigners fields (in object or blob form) and
    creates a single transaction with all BatchSigners that then gets signed and
    returned.

    Args:
        transactions: The transactions to combine `BatchSigners` values on.

    Raises:
        XRPLException: If the list of transactions provided is invalid.

    Returns:
        A single signed Transaction which has all BatchSigners from transactions within
        it.
    """
    if len(transactions) == 0:
        raise XRPLException("There were 0 transactions to combine.")

    decoded_txs: List[Transaction] = [
        Transaction.from_blob(tx) if isinstance(tx, str) else tx for tx in transactions
    ]
    for tx in decoded_txs:
        if tx.transaction_type != "Batch":
            raise XRPLException("TransactionType must be `Batch`.")
        batch = cast(Batch, tx)
        if batch.batch_signers is None or len(batch.batch_signers) == 0:
            raise XRPLException(
                "For combining Batch transaction signatures, all transactions must "
                "include a BatchSigners field containing an array of signatures."
            )
        if (
            tx.signing_pub_key != ""
            or tx.txn_signature is not None
            or tx.signers is not None
        ):
            raise XRPLException("Transaction must be unsigned.")

    batch_txs = cast(List[Batch], decoded_txs)
    _validate_batch_equivalence(batch_txs)

    return encode(_get_batch_with_all_signers(batch_txs).to_xrpl())


def _get_batch_equivalence_key(tx: Batch) -> Tuple[str, int, int, Tuple[str, ...]]:
    """
    Build a comparison key over every field bound into a Batch signature
    (XLS-56 V1_1): the outer account, sequence value, flags, and inner transaction
    IDs. Fragments that disagree on any of these were signed over different payloads
    and cannot be combined.
    """
    return (
        tx.account,
        _get_batch_seq_value(tx),
        tx._flags_to_int() or 0,
        tuple(raw_tx.get_hash() for raw_tx in tx.raw_transactions),
    )


def _validate_batch_equivalence(transactions: List[Batch]) -> None:
    example_key = _get_batch_equivalence_key(transactions[0])
    for tx in transactions[1:]:
        if _get_batch_equivalence_key(tx) != example_key:
            raise XRPLException(
                "Account, sequence, flags, and transaction hashes must be the same "
                "for all provided transactions."
            )


def _account_sort_key(account: str) -> str:
    """Sort key ordering accounts by their AccountID bytes (rippled requirement)."""
    return decode_classic_address(account).hex().upper()


def _get_batch_with_all_signers(transactions: List[Batch]) -> Batch:
    outer_account = transactions[0].account

    # Group BatchSigners by account, merging fragments that share one. A batch
    # signer cannot be the outer account (rippled: temBAD_SIGNER).
    signers_by_account: Dict[str, BatchSigner] = {}
    for tx in transactions:
        for signer in tx.batch_signers or []:
            if signer.account == outer_account:
                continue
            previous = signers_by_account.get(signer.account)
            signers_by_account[signer.account] = (
                _merge_batch_signers(previous, signer) if previous else signer
            )

    batch_signers = sorted(
        signers_by_account.values(),
        key=lambda signer: _account_sort_key(signer.account),
    )
    returned_tx_dict = transactions[0].to_dict()
    return Batch.from_dict({**returned_tx_dict, "batch_signers": batch_signers})


def _merge_batch_signers(first: BatchSigner, second: BatchSigner) -> BatchSigner:
    """
    Merge two BatchSigners that share the same account: multi-signed fragments
    have their inner ``Signers`` merged and sorted by account; identical single-
    signed fragments collapse to one; any other combination raises.
    """
    if first.signers is not None and second.signers is not None:
        inner_by_account: Dict[str, Signer] = {}
        for inner in [*first.signers, *second.signers]:
            existing = inner_by_account.get(inner.account)
            if existing is not None and existing != inner:
                raise XRPLException(
                    "Conflicting signatures for inner signer "
                    f"{inner.account} on batch account {first.account}."
                )
            inner_by_account[inner.account] = inner
        merged = sorted(
            inner_by_account.values(),
            key=lambda inner: _account_sort_key(inner.account),
        )
        return BatchSigner(account=first.account, signers=merged)

    if first.signers is None and second.signers is None:
        if (
            first.signing_pub_key == second.signing_pub_key
            and first.txn_signature == second.txn_signature
        ):
            return first
        raise XRPLException(
            f"Conflicting single-signed BatchSigners for account {first.account}."
        )

    raise XRPLException(
        "Cannot combine single-signed and multi-signed BatchSigners for account "
        f"{first.account}."
    )
