"""High-level transaction methods with XRPL transactions."""
import asyncio
from typing import List, Optional

from xrpl.asyncio.transaction import main
from xrpl.clients.sync_client import SyncClient
from xrpl.models.response import Response
from xrpl.models.transactions.transaction import Transaction
from xrpl.wallet.main import Wallet


def safe_sign_and_submit_transaction(
    transaction: Transaction,
    wallet: Wallet,
    client: SyncClient,
    autofill: bool = True,
    check_fee: bool = True,
) -> Response:
    """
    Signs a transaction (locally, without trusting external rippled nodes) and submits
    it to the XRPL.

    Args:
        transaction: the transaction to be signed and submitted.
        wallet: the wallet with which to sign the transaction.
        client: the network client with which to submit the transaction.
        autofill: whether to autofill the relevant fields. Defaults to True.
        check_fee: whether to check if the fee is higher than the expected transaction
            type fee. Defaults to True.

    Returns:
        The response from the ledger.
    """
    return asyncio.run(
        main.safe_sign_and_submit_transaction(
            transaction,
            wallet,
            client,
            autofill,
            check_fee,
        )
    )


def submit_transaction(
    transaction: Transaction,
    client: SyncClient,
) -> Response:
    """
    Submits a transaction to the ledger.

    Args:
        transaction: the Transaction to be submitted.
        client: the network client with which to submit the transaction.

    Returns:
        The response from the ledger.

    Raises:
        XRPLRequestFailureException: if the rippled API call fails.
    """
    return asyncio.run(
        main.submit_transaction(
            transaction,
            client,
        )
    )


def safe_sign_transaction(
    transaction: Transaction,
    wallet: Wallet,
    check_fee: bool = True,
) -> Transaction:
    """
    Signs a transaction locally, without trusting external rippled nodes.

    Args:
        transaction: the transaction to be signed.
        wallet: the wallet with which to sign the transaction.
        check_fee: whether to check if the fee is higher than the expected transaction
            type fee. Defaults to True.

    Returns:
        The signed transaction.
    """
    return asyncio.run(
        main.safe_sign_transaction(
            transaction,
            wallet,
            check_fee,
        )
    )


def safe_sign_and_autofill_transaction(
    transaction: Transaction,
    wallet: Wallet,
    client: SyncClient,
    check_fee: bool = True,
) -> Transaction:
    """
    Signs a transaction locally, without trusting external rippled nodes. Autofills
    relevant fields.

    Args:
        transaction: the transaction to be signed.
        wallet: the wallet with which to sign the transaction.
        client: a network client.
        check_fee: whether to check if the fee is higher than the expected transaction
            type fee. Defaults to True.

    Returns:
        The signed transaction.
    """
    return asyncio.run(
        main.safe_sign_and_autofill_transaction(
            transaction,
            wallet,
            client,
            check_fee,
        )
    )


def autofill(
    transaction: Transaction, client: SyncClient, signers_count: Optional[int] = None
) -> Transaction:
    """
    Autofills fields in a transaction. This will set `sequence`, `fee`, and
    `last_ledger_sequence` according to the current state of the server this Client is
    connected to. It also converts all X-Addresses to classic addresses.

    Args:
        transaction: the transaction to be signed.
        client: a network client.
        signers_count: the expected number of signers for this transaction.
            Only used for multisigned transactions.

    Returns:
        The autofilled transaction.
    """
    return asyncio.run(
        main.autofill(
            transaction,
            client,
            signers_count,
        )
    )


def safe_sign_transaction_with_multisign(
    transaction: Transaction,
    wallet: Wallet,
) -> str:
    """
    Signs a transaction with to be used for multisigning.

    Args:
        transaction: the transaction to be signed.
        wallet: the wallet with which to sign the transaction.

    Returns:
        The signed transaction blob.
    """
    return asyncio.run(
        main.safe_sign_transaction_with_multisign(
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
        main.multisign(
            transaction,
            tx_blobs,
        )
    )
