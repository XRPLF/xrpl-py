"""High-level transaction methods with XRPL transactions."""

import asyncio
from typing import Optional

from typing_extensions import TypeVar

from xrpl.asyncio.transaction import main
from xrpl.clients.sync_client import SyncClient
from xrpl.models.response import Response
from xrpl.models.transactions.transaction import Transaction
from xrpl.wallet.main import Wallet

T = TypeVar("T", bound=Transaction, default=Transaction)


def sign_and_submit(
    transaction: Transaction,
    client: SyncClient,
    wallet: Wallet,
    autofill: bool = True,
    check_fee: bool = True,
) -> Response:
    """
    Signs a transaction (locally, without trusting external rippled nodes) and submits
    it to the XRPL.

    Args:
        transaction: the transaction to be signed and submitted.
        client: the network client with which to submit the transaction.
        wallet: the wallet with which to sign the transaction.
        autofill: whether to autofill the relevant fields. Defaults to True.
        check_fee: whether to check if the fee is higher than the expected transaction
            type fee. Defaults to True.

    Returns:
        The response from the ledger.
    """
    return asyncio.run(
        main.sign_and_submit(
            transaction,
            client,
            wallet,
            autofill,
            check_fee,
        )
    )


def submit(
    transaction: Transaction,
    client: SyncClient,
    *,
    fail_hard: bool = False,
) -> Response:
    """
    Submits a transaction to the ledger.

    Args:
        transaction: the Transaction to be submitted.
        client: the network client with which to submit the transaction.
        fail_hard: an optional boolean. If True, and the transaction fails for
            the initial server, do not retry or relay the transaction to other
            servers. Defaults to False.

    Returns:
        The response from the ledger.

    Raises:
        XRPLRequestFailureException: if the rippled API call fails.
    """
    return asyncio.run(
        main.submit(
            transaction,
            client,
            fail_hard=fail_hard,
        )
    )


sign = main.sign


def autofill_and_sign(
    transaction: T,
    client: SyncClient,
    wallet: Wallet,
    check_fee: bool = True,
) -> T:
    """
    Signs a transaction locally, without trusting external rippled nodes. Autofills
    relevant fields.

    Args:
        transaction: the transaction to be signed.
        client: a network client.
        wallet: the wallet with which to sign the transaction.
        check_fee: whether to check if the fee is higher than the expected transaction
            type fee. Defaults to True.

    Returns:
        The signed transaction.
    """
    return asyncio.run(
        main.autofill_and_sign(
            transaction,
            client,
            wallet,
            check_fee,
        )
    )


def autofill(
    transaction: T, client: SyncClient, signers_count: Optional[int] = None
) -> T:
    """
    Autofills fields in a transaction. This will set all autofill-able fields according
    to the current state of the server this Client is connected to. For Batch
    transactions, it will also handle autofilling inner transactions. It also converts
    all X-Addresses to classic addresses.

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


def simulate(
    transaction: Transaction,
    client: SyncClient,
    *,
    binary: bool = False,
) -> Response:
    """
    Simulates a transaction without actually submitting it to the network.

    Args:
        transaction: The transaction to simulate.
        client: The network client with which to submit the transaction.
        binary: Whether the return data should be encoded in the XRPL's binary format.
            Defaults to False.

    Raises:
        XRPLRequestFailureException: If the transaction fails in the simulated scenario.

    Returns:
        The response from the ledger.
    """
    return asyncio.run(
        main.simulate(
            transaction,
            client,
            binary=binary,
        )
    )
