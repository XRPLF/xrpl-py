"""High-level transaction methods with XRPL transactions."""
import asyncio

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


def autofill(transaction: Transaction, client: SyncClient) -> Transaction:
    """
    Autofills fields in a transaction. This will set `sequence`, `fee`, and
    `last_ledger_sequence` according to the current state of the server this Client is
    connected to. It also converts all X-Addresses to classic addresses.

    Args:
        transaction: the transaction to be signed.
        client: a network client.

    Returns:
        The autofilled transaction.
    """
    return asyncio.run(
        main.autofill(
            transaction,
            client,
        )
    )
