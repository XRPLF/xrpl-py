"""High-level methods to obtain information about account transaction history."""
from typing import Any, Dict, List, cast

from xrpl.clients import Client, XRPLRequestFailureException
from xrpl.models.requests import AccountTx
from xrpl.models.response import Response


def get_latest_transaction(account: str, client: Client) -> Response:
    """
    Fetches the most recent transaction on the ledger associated with an account.

    Args:
        account: the classic address of the account.
        client: the network client used to communicate with a rippled node.

    Returns:
        The Response object containing the transaction info.

    Raises:
        XRPLRequestFailureException: if the transaction fails.
    """
    # max == -1 means that it's the most recent validated ledger version
    response = client.request(AccountTx(account=account, ledger_index_max=-1, limit=1))
    if not response.is_successful():
        result = cast(Dict[str, Any], response.result)
        raise XRPLRequestFailureException(result)
    return response


def get_account_transactions(address: str, client: Client) -> List[Dict[str, Any]]:
    """
    Query the ledger for a list of transactions that involved a given account.

    Args:
        address: the account to query.
        client: the network client used to make network calls.

    Returns:
        The transaction history for the address.

    Raises:
        XRPLRequestFailureException: if the transaction fails.
    """
    request = AccountTx(account=address)
    response = client.request(request)
    result = cast(Dict[str, Any], response.result)
    if not response.is_successful():
        raise XRPLRequestFailureException(result)
    return cast(List[Dict[str, Any]], result["transactions"])


def get_account_payment_transactions(
    address: str, client: Client
) -> List[Dict[str, Any]]:
    """
    Query the ledger for a list of payment transactions that involved a given account.

    Args:
        address: the account to query.
        client: the network client used to make network calls.

    Returns:
        The payment transaction history for the address.
    """
    all_transactions = get_account_transactions(address, client)
    return [tx for tx in all_transactions if tx["tx"]["TransactionType"] == "Payment"]
