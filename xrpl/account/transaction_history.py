"""High-level methods to obtain information about account transaction history."""

from xrpl.clients import Client
from xrpl.models.requests import AccountTx
from xrpl.models.response import Response


def get_account_transactions(address: str, client: Client) -> Response:
    """
    Query the ledger for a list of transactions that involved a given account.

    Args:
        address: the account to query.
        client: the network client used to make network calls.

    Returns:
        The transaction history for the address.
    """
    request = AccountTx(account=address)
    return client.request(request)
