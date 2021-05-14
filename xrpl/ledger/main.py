"""High-level ledger methods with the XRPL ledger."""

import asyncio

from xrpl.async_support.ledger import main
from xrpl.clients import Client


def get_latest_validated_ledger_sequence(client: Client) -> int:
    """
    Returns the sequence number of the latest validated ledger.

    Args:
        client: The network client to use to send the request.

    Returns:
        The sequence number of the latest validated ledger.

    Raises:
        XRPLRequestFailureException: if the rippled API call fails.
    """
    return asyncio.run(main.get_latest_validated_ledger_sequence(client))


def get_latest_open_ledger_sequence(client: Client) -> int:
    """
    Returns the sequence number of the latest open ledger.

    Args:
        client: The network client to use to send the request.

    Returns:
        The sequence number of the latest open ledger.

    Raises:
        XRPLRequestFailureException: if the rippled API call fails.
    """
    return asyncio.run(main.get_latest_open_ledger_sequence(client))


def get_fee(client: Client) -> str:
    """
    Query the ledger for the current minimum transaction fee.

    Args:
        client: the network client used to make network calls.

    Returns:
        The minimum fee for transactions.

    Raises:
        XRPLRequestFailureException: if the rippled API call fails.
    """
    return asyncio.run(main.get_fee(client))
