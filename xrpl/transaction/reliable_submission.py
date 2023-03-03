"""High-level reliable submission methods with XRPL transactions."""

import asyncio

from xrpl.asyncio.transaction import (
    send_reliable_submission as async_send_reliable_submission,
)
from xrpl.asyncio.transaction import submit_and_wait as async_submit_and_wait
from xrpl.clients.sync_client import SyncClient
from xrpl.models.response import Response
from xrpl.models.transactions.transaction import Transaction
from xrpl.wallet.main import Wallet


def send_reliable_submission(transaction: Transaction, client: SyncClient) -> Response:
    """
    Submits a transaction and verifies that it has been included in a validated ledger
    (or has errored/will not be included for some reason).

    `See Reliable Transaction Submission
    <https://xrpl.org/reliable-transaction-submission.html>`_

    Note: This cannot be used with a standalone rippled node, because ledgers do not
    close automatically.

    Args:
        transaction: the signed transaction to submit to the ledger. Requires a
            `last_ledger_sequence` param.
        client: the network client used to submit the transaction to a rippled node.

    Returns:
        The response from a validated ledger.
    """
    return asyncio.run(async_send_reliable_submission(transaction, client))


def submit_and_wait(
    transaction: Transaction,
    wallet: Wallet,
    client: SyncClient,
    check_fee: bool = True,
    autofill: bool = True,
) -> Response:
    """
    Signs a transaction (locally, without trusting external rippled nodes), submits,
    and verifies that it has been included in a validated ledger (or has errored
    /will not be included for some reason).
    `See Reliable Transaction Submission
    <https://xrpl.org/reliable-transaction-submission.html>`_

    Args:
        transaction: the transaction to be signed and submitted.
        wallet: the wallet with which to sign the transaction.
        client: the network client with which to submit the transaction.
        check_fee: an optional bolean indicating whether to check if the fee is
            higher than the expected transaction type fee. Defaults to True.
        autofill: an optional boolean indicating whether to autofill the
            transaction. Defaults to True.

    Returns:
        The response from the ledger.
    """
    return asyncio.run(
        async_submit_and_wait(
            transaction,
            wallet,
            client,
            check_fee,
            autofill,
        )
    )
