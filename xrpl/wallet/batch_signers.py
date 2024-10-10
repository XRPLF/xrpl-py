"""Helper functions for signing multi-account Batch transactions."""

from typing import Any, Dict, Optional

from xrpl.constants import XRPLException
from xrpl.core.binarycodec import encode_for_batch
from xrpl.core.keypairs import sign
from xrpl.models.transactions import Batch, Signer
from xrpl.models.transactions.batch import BatchSigner
from xrpl.wallet import Wallet


def sign_multiaccount_batch(
    wallet: Wallet, transaction: Batch, multisign: Optional[bool] = False
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

    fields_to_sign: Dict[str, Any] = {
        "flags": transaction.flags,
        "tx_ids": transaction.tx_ids,
    }
    if multisign:
        signer = Signer(
            account=wallet.address,
            signing_pub_key=wallet.public_key,
            txn_signature=sign(encode_for_batch(fields_to_sign), wallet.private_key),
        )
        batch_signer = BatchSigner(account=wallet.address, signers=[signer])
    else:
        batch_signer = BatchSigner(
            account=wallet.address,
            signing_pub_key=wallet.public_key,
            txn_signature=sign(encode_for_batch(fields_to_sign), wallet.private_key),
        )

    transaction_dict = transaction.to_dict()
    transaction_dict["batch_signers"] = [batch_signer]

    return Batch.from_dict(transaction_dict)
