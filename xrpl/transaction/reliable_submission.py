"""High-level reliable submission methods with XRPL transactions."""

import asyncio

from xrpl.asyncio.transaction import (
    send_reliable_submission as async_send_reliable_submission,
)
from xrpl.clients.sync_client import SyncClient
from xrpl.models.response import Response
from xrpl.models.transactions.transaction import Transaction


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
