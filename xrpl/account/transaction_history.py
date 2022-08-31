"""High-level methods to obtain information about account transaction history."""
import asyncio
from typing import Any, Dict, List, Optional, Tuple

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


def get_account_transactions_with_marker(
    address: str, client: SyncClient, marker: Optional[Any] = None
) -> Tuple[List[Dict[str, Any]], Any]:
    """
    Query the ledger for a list of transactions that involved a given account.

    Args:
        address: the account to query.
        client: the network client used to make network calls.
        marker: fetches the next set of data from the server. The type of
            marker is intentionally undefined in the spec and is chosen
            by each server.

    Returns:
        The most recent set of transactions for this address from the marker, along
        with a new marker if there are more results to fetch from the server. Passing
        the marker back in will fetch the next set of results. If there are no more
        results, the marker will be None.

    Raises:
        XRPLRequestFailureException: if the transaction fails.
    """
    return asyncio.run(
        transaction_history.get_account_transactions_with_marker(
            address, client, marker
        )
    )


def get_account_transactions(
    address: str, client: SyncClient, marker: Optional[Any] = None
) -> List[Dict[str, Any]]:
    """
    Query the ledger for a list of transactions that involved a given account.

    Args:
        address: the account to query.
        client: the network client used to make network calls.
        marker: fetches the next set of data from the server. The type of
            marker is intentionally undefined in the spec and is chosen
            by each server.

    Returns:
        The transaction history for the address.

    Raises:
        XRPLRequestFailureException: if the transaction fails.
    """
    return asyncio.run(
        transaction_history.get_account_transactions(address, client, marker)
    )


def get_account_payment_transactions_with_marker(
    address: str, client: SyncClient, marker: Optional[Any] = None
) -> Tuple[List[Dict[str, Any]], Any]:
    """
    Query the ledger for a list of payment transactions that involved a given account.

    Args:
        address: the account to query.
        client: the network client used to make network calls.
        marker: fetches the next set of data from the server. The type of
            marker is intentionally undefined in the spec and is chosen
            by each server.

    Returns:
        The payment transaction history for the address, along with a marker if there
        are more results to fetch from the server. Passing the marker back in will
        fetch the next set of results. If there are no more results, the marker will
        be None.
    """
    return asyncio.run(
        transaction_history.get_account_payment_transactions_with_marker(
            address, client, marker
        )
    )


def get_account_payment_transactions(
    address: str, client: SyncClient, marker: Optional[Any] = None
) -> List[Dict[str, Any]]:
    """
    Query the ledger for a list of payment transactions that involved a given account.

    Args:
        address: the account to query.
        client: the network client used to make network calls.
        marker: fetches the next set of data from the server. The type of
            marker is intentionally undefined in the spec and is chosen
            by each server.

    Returns:
        The payment transaction history for the address.
    """
    return asyncio.run(
        transaction_history.get_account_payment_transactions(address, client, marker)
    )
