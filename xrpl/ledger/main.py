"""High-level ledger methods with the XRPL ledger."""

import asyncio

# from xrpl.clients.sync_client import SyncClient
import xrpl.clients.sync_client as sync_client_ref
from xrpl.asyncio.ledger import main


def get_latest_validated_ledger_sequence(client: sync_client_ref.SyncClient) -> int:
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


def get_latest_open_ledger_sequence(client: sync_client_ref.SyncClient) -> int:
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


def get_fee(client: sync_client_ref.SyncClient) -> str:
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
