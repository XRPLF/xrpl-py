"""High-level methods to obtain information about accounts."""

import asyncio
from typing import Dict, Union

from deprecated.sphinx import deprecated

from xrpl.asyncio.account import main
from xrpl.clients.sync_client import SyncClient
from xrpl.models.response import Response


def does_account_exist(
    address: str, client: SyncClient, ledger_index: Union[str, int] = "validated"
) -> bool:
    """
    Query the ledger for whether the account exists.

    Args:
        address: the account to query.
        client: the network client used to make network calls.
        ledger_index: The ledger index to use for the request. Must be an integer
            ledger value or "current" (the current working version), "closed" (for the
            closed-and-proposed version), or "validated" (the most recent version
            validated by consensus). The default is "validated".

    Returns:
        Whether the account exists on the ledger.

    Raises:
        XRPLRequestFailureException: if the transaction fails.
    """
    return asyncio.run(main.does_account_exist(address, client, ledger_index))


def get_next_valid_seq_number(
    address: str, client: SyncClient, ledger_index: Union[str, int] = "current"
) -> int:
    """
    Query the ledger for the next available sequence number for an account.

    Args:
        address: the account to query.
        client: the network client used to make network calls.
        ledger_index: The ledger index to use for the request. Must be an integer
            ledger value or "current" (the current working version), "closed" (for the
            closed-and-proposed version), or "validated" (the most recent version
            validated by consensus). The default is "current".

    Returns:
        The next valid sequence number for the address.
    """
    return asyncio.run(main.get_next_valid_seq_number(address, client, ledger_index))


def get_balance(
    address: str, client: SyncClient, ledger_index: Union[str, int] = "validated"
) -> int:
    """
    Query the ledger for the balance of the given account.

    Args:
        address: the account to query.
        client: the network client used to make network calls.
        ledger_index: The ledger index to use for the request. Must be an integer
            ledger value or "current" (the current working version), "closed" (for the
            closed-and-proposed version), or "validated" (the most recent version
            validated by consensus). The default is "validated".

    Returns:
        The balance of the address.
    """
    return asyncio.run(main.get_balance(address, client, ledger_index))


def get_account_root(
    address: str, client: SyncClient, ledger_index: Union[str, int] = "validated"
) -> Dict[str, Union[int, str]]:
    """
    Query the ledger for the AccountRoot object associated with a given address.

    Args:
        address: the account to query.
        client: the network client used to make network calls.
        ledger_index: The ledger index to use for the request. Must be an integer
            ledger value or "current" (the current working version), "closed" (for the
            closed-and-proposed version), or "validated" (the most recent version
            validated by consensus). The default is "validated".

    Returns:
        The AccountRoot dictionary for the address.
    """
    return asyncio.run(main.get_account_root(address, client, ledger_index))


@deprecated(
    reason="Sending an AccountInfo request directly is just as easy to use.",
    version="1.8.0",
)
def get_account_info(
    address: str, client: SyncClient, ledger_index: Union[str, int] = "validated"
) -> Response:
    """
    Query the ledger for account info of given address.

    Args:
        address: the account to query.
        client: the network client used to make network calls.
        ledger_index: The ledger index to use for the request. Must be an integer
            ledger value or "current" (the current working version), "closed" (for the
            closed-and-proposed version), or "validated" (the most recent version
            validated by consensus). The default is "validated".

    Returns:
        The account info for the address.

    Raises:
        XRPLRequestFailureException: if the rippled API call fails.
    """
    return asyncio.run(main.get_account_info(address, client, ledger_index))
