"""High-level methods to obtain information about account transaction history."""
from typing import Any, Dict, List, cast

from xrpl.clients import Client, XRPLTransactionFailureException
from xrpl.models.requests import AccountTx


def get_account_transactions(address: str, client: Client) -> List[Dict[str, Any]]:
    """
    Query the ledger for a list of transactions that involved a given account.

    Args:
        address: the account to query.
        client: the network client used to make network calls.

    Returns:
        The transaction history for the address.

    Raises:
        XRPLTransactionFailureException: if the transaction fails.
    """
    request = AccountTx(account=address)
    response = client.request(request)
    result = cast(Dict[str, Any], response.result)
    if not response.is_successful():
        raise XRPLTransactionFailureException(result["error"], result["error_message"])
    return cast(List[Dict[str, Any]], result["transactions"])
