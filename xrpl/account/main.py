"""High-level methods to obtain information about accounts."""

from typing import Any, Dict, Union, cast

from xrpl.clients import Client
from xrpl.models.requests import AccountInfo
from xrpl.models.response import Response


def get_next_valid_seq_number(address: str, client: Client) -> int:
    """
    Query the ledger for the next available sequence number for an account.

    Args:
        address: the account to query.
        client: the network client used to make network calls.

    Returns:
        The next valid sequence number for the address.
    """
    return cast(int, get_account_root(address, client)["Sequence"])


def get_balance(address: str, client: Client) -> int:
    """
    Query the ledger for the balance of the given account.

    Args:
        address: the account to query.
        client: the network client used to make network calls.

    Returns:
        The balance of the address.
    """
    return cast(int, get_account_root(address, client)["Balance"])


def get_account_root(address: str, client: Client) -> Dict[str, Union[int, str]]:
    """
    Query the ledger for the AccountRoot object associated with a given address.

    Args:
        address: the account to query.
        client: the network client used to make network calls.

    Returns:
        The AccountRoot dictionary for the address.
    """
    account_info = get_account_info(address, client)
    result = cast(Dict[str, Any], account_info.result)
    return cast(Dict[str, Union[int, str]], result["account_data"])


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
