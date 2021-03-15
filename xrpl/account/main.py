"""High-level methods to obtain information about accounts."""

from typing import Any, Dict, cast

from xrpl.clients import Client
from xrpl.models.requests.account_info import AccountInfo
from xrpl.models.requests.fee import Fee
from xrpl.models.response import Response


def get_fee(client: Client) -> str:
    """
    Query the ledger for the current minimum transaction fee.

    Args:
        client: the network client used to make network calls.

    Returns:
        The minimum fee for transactions.
    """
    response = client.request(Fee())
    result = cast(Dict[str, Any], response.result)
    return cast(str, result["drops"]["minimum_fee"])


def get_next_valid_seq_number(address: str, client: Client) -> int:
    """
    Query the ledger for the next available sequence number for an account.

    Args:
        address: the account to query.
        client: the network client used to make network calls.

    Returns:
        The next valid sequence number for the address.
    """
    account_info = get_account_info(address, client)
    result = cast(Dict[str, Any], account_info.result)
    return cast(int, result["account_data"]["Sequence"])


def get_balance(address: str, client: Client) -> int:
    """
    Query the ledger for the balance of the given account.

    Args:
        address: the account to query.
        client: the network client used to make network calls.

    Returns:
        The balance of the address.
    """
    account_info = get_account_info(address, client)
    result = cast(Dict[str, Any], account_info.result)
    return cast(int, result["account_data"]["Balance"])


def get_account_info(address: str, client: Client) -> Response:
    """
    Query the ledger for account info of given address.

    Args:
        address: the account to query.
        client: the network client used to make network calls.

    Returns:
        The account info for the address.
    """
    return client.request(
        AccountInfo(
            account=address,
            ledger_index="validated",
        )
    )
