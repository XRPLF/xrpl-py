"""High-level ledger methods with the XRPL ledger."""

from typing import Any, Dict, cast

from xrpl.asyncio.clients import Client, XRPLRequestFailureException
from xrpl.models.requests import Fee, Ledger


async def get_latest_validated_ledger_sequence(client: Client) -> int:
    """
    Returns the sequence number of the latest validated ledger.

    Args:
        client: The network client to use to send the request.

    Returns:
        The sequence number of the latest validated ledger.

    Raises:
        XRPLRequestFailureException: if the rippled API call fails.
    """
    response = await client.request_impl(Ledger(ledger_index="validated"))
    result = cast(Dict[str, Any], response.result)
    if response.is_successful():
        return cast(int, result["ledger_index"])

    raise XRPLRequestFailureException(result)


async def get_latest_open_ledger_sequence(client: Client) -> int:
    """
    Returns the sequence number of the latest open ledger.

    Args:
        client: The network client to use to send the request.

    Returns:
        The sequence number of the latest open ledger.

    Raises:
        XRPLRequestFailureException: if the rippled API call fails.
    """
    response = await client.request_impl(Ledger(ledger_index="open"))
    result = cast(Dict[str, Any], response.result)
    if response.is_successful():
        return cast(int, result["ledger_index"])

    raise XRPLRequestFailureException(result)


async def get_fee(client: Client) -> str:
    """
    Query the ledger for the current minimum transaction fee.

    Args:
        client: the network client used to make network calls.

    Returns:
        The minimum fee for transactions.

    Raises:
        XRPLRequestFailureException: if the rippled API call fails.
    """
    response = await client.request_impl(Fee())
    result = cast(Dict[str, Any], response.result)
    if response.is_successful():
        return cast(str, result["drops"]["minimum_fee"])

    raise XRPLRequestFailureException(result)
