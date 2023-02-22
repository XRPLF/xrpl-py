"""High-level transaction methods with XRPL transactions."""
import asyncio
from typing import Optional

from xrpl.asyncio.transaction import main
from xrpl.clients.sync_client import SyncClient
from xrpl.models.response import Response
from xrpl.models.transactions.transaction import Transaction
from xrpl.wallet.main import Wallet


def sign_and_submit(
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
        main.sign_and_submit(
            transaction,
            wallet,
            client,
            autofill,
            check_fee,
        )
    )


safe_sign_and_submit_transaction = sign_and_submit


def submit(
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
        main.submit(
            transaction,
            client,
        )
    )


submit_transaction = submit


def sign(
    transaction: Transaction,
    wallet: Wallet,
    check_fee: bool = True,
    multisign: bool = False,
) -> Transaction:
    """
    Signs a transaction locally, without trusting external rippled nodes.

    Args:
        transaction: the transaction to be signed.
        wallet: the wallet with which to sign the transaction.
        check_fee: whether to check if the fee is higher than the expected transaction
            type fee. Defaults to True.
        multisign: whether to sign the transaction for a multisignature transaction.

    Returns:
        The signed transaction.
    """
    return asyncio.run(
        main.sign(
            transaction,
            wallet,
            check_fee,
            multisign,
        )
    )


safe_sign_transaction = sign


def autofill_and_sign(
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
        main.autofill_and_sign(
            transaction,
            wallet,
            client,
            check_fee,
        )
    )


safe_sign_and_autofill_transaction = autofill_and_sign


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
