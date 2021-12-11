"""High-level ledger methods with the XRPL ledger."""

import asyncio
from typing import Optional

from xrpl.asyncio.ledger import main
from xrpl.clients.sync_client import SyncClient


def get_latest_validated_ledger_sequence(client: SyncClient) -> int:
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


def get_latest_open_ledger_sequence(client: SyncClient) -> int:
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


def get_fee(client: SyncClient, max_fee: Optional[float] = 2) -> str:
    """
    Query the ledger for the current minimum transaction fee.

    Args:
        client: the network client used to make network calls.
        max_fee: The maximum fee in XRP that the user wants to pay. If load gets too
            high, then the fees will not scale past the maximum fee. If None, there is
            no ceiling for the fee. The default is 2 XRP.

    Returns:
        The minimum fee for transactions.

    Raises:
        XRPLRequestFailureException: if the rippled API call fails.
    """
    return asyncio.run(main.get_fee(client, max_fee))
