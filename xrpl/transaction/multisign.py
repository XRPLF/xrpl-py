"""Multisign transaction methods with XRPL transactions."""
import asyncio
from typing import List

from xrpl.asyncio.transaction import multisign as multisign_async
from xrpl.asyncio.transaction import sign_for_multisign as sign_for_multisign_async
from xrpl.models.transactions.transaction import Transaction
from xrpl.wallet.main import Wallet


def sign_for_multisign(
    transaction: Transaction,
    wallet: Wallet,
) -> str:
    """
    Signs a transaction to be used for multisigning.

    Args:
        transaction: the transaction to be signed.
        wallet: the wallet with which to sign the transaction.

    Returns:
        The signed transaction blob.
    """
    return asyncio.run(
        sign_for_multisign_async(
            transaction,
            wallet,
        )
    )


def multisign(transaction: Transaction, tx_blobs: List[str]) -> Transaction:
    """
    Takes several transactions with Signer fields (blob form) and creates a
    single transaction with all Signers that then gets signed and returned.

    Args:
        transaction: the transaction to be signed.
        tx_blobs: a list of signed transactions (in blob form) to combine into
            a single signed transaction.

    Returns:
        The multisigned transaction.
    """
    return asyncio.run(
        multisign_async(
            transaction,
            tx_blobs,
        )
    )
