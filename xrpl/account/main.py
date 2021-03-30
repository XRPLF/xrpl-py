"""High-level methods to obtain information about accounts."""

from typing import Any, Dict, Union, cast

from xrpl.clients import Client, XRPLRequestFailureException
from xrpl.models.requests import AccountInfo
from xrpl.models.response import Response


def does_account_exist(address: str, client: Client) -> bool:
    """
    Query the ledger for whether the account exists.

    Args:
        address: the account to query.
        client: the network client used to make network calls.

    Returns:
        Whether the account exists on the ledger.

    Raises:
        XRPLRequestFailureException: if the transaction fails.
    """
    try:
        get_account_info(address, client)
        return True
    except XRPLRequestFailureException as e:
        if e.error == "actNotFound":
            # error code for if the account is not found on the ledger
            return False
        raise


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
    return int(get_account_root(address, client)["Balance"])


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

    Raises:
        XRPLRequestFailureException: if the rippled API call fails.
    """
    response = client.request(
        AccountInfo(
            account=address,
            ledger_index="validated",
        )
    )
    if response.is_successful():
        return response

    result = cast(Dict[str, Any], response.result)
    raise XRPLRequestFailureException(result)
