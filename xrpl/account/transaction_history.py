"""High-level methods to obtain information about account transaction history."""
import asyncio
from typing import Any, Dict, List

from deprecated.sphinx import deprecated

from xrpl.asyncio.account import transaction_history
from xrpl.clients.sync_client import SyncClient
from xrpl.models.response import Response


def get_latest_transaction(account: str, client: SyncClient) -> Response:
    """
    Fetches the most recent transaction on the ledger associated with an account.

    Args:
        account: the account to query.
        client: the network client used to communicate with a rippled node.

    Returns:
        The Response object containing the transaction info.

    Raises:
        XRPLRequestFailureException: if the transaction fails.
    """
    return asyncio.run(transaction_history.get_latest_transaction(account, client))


@deprecated(
    reason="Sending an AccountTx request directly allows you to page through all "
    "results and is just as easy to use.",
    version="1.6.0",
)
def get_account_transactions(address: str, client: SyncClient) -> List[Dict[str, Any]]:
    """
    Query the ledger for a list of transactions that involved a given account.
    To access more than just the first page of results, use the :class:`AccountTx`
    request directly.

    Args:
        address: the account to query.
        client: the network client used to make network calls.

    Returns:
        The most recent transaction history for the address. For the full history,
        page through the :class:`AccountTx` request directly.

    Raises:
        XRPLRequestFailureException: if the transaction fails.
    """
    return asyncio.run(transaction_history.get_account_transactions(address, client))


@deprecated(
    reason="Sending an AccountTx request directly and filtering for payments allows "
    "you to page through all results and is just as easy to use.",
    version="1.8.0",
)
def get_account_payment_transactions(
    address: str, client: SyncClient
) -> List[Dict[str, Any]]:
    """
    Query the ledger for a list of payment transactions that involved a given account.
    To access more than just the first page of results, use the :class:`AccountTx`
    request directly then filter for transactions with a "Payment" TransactionType.

    Args:
        address: the account to query.
        client: the network client used to make network calls.

    Returns:
        The first page of payment transaction history for the address. For the full
        history, page through the :class:`AccountTx` request directly.
    """
    return asyncio.run(
        transaction_history.get_account_payment_transactions(address, client)
    )
