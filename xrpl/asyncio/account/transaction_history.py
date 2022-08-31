"""High-level methods to obtain information about account transaction history."""
from typing import Any, Dict, List, Optional, Tuple, cast

from xrpl.asyncio.clients import Client, XRPLRequestFailureException
from xrpl.core.addresscodec import is_valid_xaddress, xaddress_to_classic_address
from xrpl.models.requests import AccountTx
from xrpl.models.response import Response


async def get_latest_transaction(account: str, client: Client) -> Response:
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
    # max == -1 means that it's the most recent validated ledger version
    if is_valid_xaddress(account):
        account, _, _ = xaddress_to_classic_address(account)
    response = await client.request_impl(
        AccountTx(account=account, ledger_index_max=-1, limit=1)
    )
    if not response.is_successful():
        raise XRPLRequestFailureException(response.result)
    return response


async def get_account_transactions_with_marker(
    address: str, client: Client, marker: Optional[Any] = None
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
    if is_valid_xaddress(address):
        address, _, _ = xaddress_to_classic_address(address)
    request = AccountTx(account=address, marker=marker)
    response = await client.request_impl(request)
    if not response.is_successful():
        raise XRPLRequestFailureException(response.result)
    return (
        cast(List[Dict[str, Any]], response.result["transactions"]),
        response.result.get("marker"),
    )


async def get_account_transactions(
    address: str, client: Client, marker: Optional[Any] = None
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
    (transactions, _) = await get_account_payment_transactions_with_marker(
        address, client, marker
    )
    return transactions


async def get_account_payment_transactions_with_marker(
    address: str, client: Client, marker: Optional[Any] = None
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
        The most recent set of payment transactions for this address from the marker,
        along with a new marker if there are more results to fetch from the server.
        Passing the marker back in will fetch the next set of results. If there are
        no more results, the marker will be None.
    """
    (all_transactions, marker) = await get_account_transactions_with_marker(
        address, client, marker
    )
    return (
        [tx for tx in all_transactions if tx["tx"]["TransactionType"] == "Payment"],
        marker,
    )


async def get_account_payment_transactions(
    address: str, client: Client, marker: Optional[Any] = None
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
    (transactions, _) = await get_account_payment_transactions_with_marker(
        address, client, marker
    )
    return transactions
