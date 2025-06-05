"""Helper functions for signing multi-account Batch transactions."""

from typing import List, Union, cast

from xrpl.constants import XRPLException
from xrpl.core.addresscodec.codec import decode_classic_address
from xrpl.core.binarycodec import encode, encode_for_signing_batch
from xrpl.core.binarycodec.main import BatchSigningDict
from xrpl.core.keypairs import sign
from xrpl.models.transactions import Batch, Signer, Transaction
from xrpl.models.transactions.batch import BatchSigner
from xrpl.wallet import Wallet


def sign_multiaccount_batch(
    wallet: Wallet, transaction: Batch, multisign: bool = False
) -> Batch:
    """
    Sign a multi-account Batch transaction.

    Args:
        wallet: Wallet instance.
        transaction: The Batch transaction to sign.
        multisign: Specify true/false to use multisign. Defaults to False.

    Raises:
        XRPLException: If the wallet signing the transaction doesn't have an account in
            the Batch.

    Returns:
        The Batch transaction with the BatchSigner included.
    """
    involved_accounts = set(tx.account for tx in transaction.raw_transactions)
    if wallet.address not in involved_accounts:
        raise XRPLException("Must be signing for an address included in the Batch.")

    fields_to_sign: BatchSigningDict = {
        "flags": transaction._flags_to_int() or 0,
        "transaction_ids": [tx.get_hash() for tx in transaction.raw_transactions],
    }
    if multisign:
        signer = Signer(
            account=wallet.address,
            signing_pub_key=wallet.public_key,
            txn_signature=sign(
                encode_for_signing_batch(fields_to_sign), wallet.private_key
            ),
        )
        batch_signer = BatchSigner(account=wallet.address, signers=[signer])
    else:
        batch_signer = BatchSigner(
            account=wallet.address,
            signing_pub_key=wallet.public_key,
            txn_signature=sign(
                encode_for_signing_batch(fields_to_sign), wallet.private_key
            ),
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


def _validate_batch_equivalence(transactions: List[Batch]) -> None:
    example_tx = transactions[0]
    for tx in transactions:
        if (
            tx.flags != example_tx.flags
            or tx.raw_transactions != example_tx.raw_transactions
        ):
            raise XRPLException(
                "Flags and RawTransactions are not the same for all provided "
                "transactions."
            )


def _get_batch_with_all_signers(transactions: List[Batch]) -> Batch:
    batch_signers = [
        signer
        for tx in transactions
        if tx.batch_signers is not None
        for signer in tx.batch_signers
        if signer.account != transactions[0].account
    ]
    batch_signers.sort(
        key=lambda signer: decode_classic_address(signer.account).hex().upper()
    )
    returned_tx_dict = transactions[0].to_dict()
    return Batch.from_dict({**returned_tx_dict, "batch_signers": batch_signers})
