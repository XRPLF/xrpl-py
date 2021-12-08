"""High-level ledger methods with the XRPL ledger."""

from typing import cast

from xrpl.asyncio.clients import Client, XRPLRequestFailureException
from xrpl.models.requests import Ledger, ServerInfo


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
    if response.is_successful():
        return cast(int, response.result["ledger_index"])

    raise XRPLRequestFailureException(response.result)


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
    if response.is_successful():
        return cast(int, response.result["ledger_index"])

    raise XRPLRequestFailureException(response.result)


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
    response = await client.request_impl(ServerInfo())
    if not response.is_successful():
        raise XRPLRequestFailureException(response.result)

    server_info = response.result["info"]
    if "validated_ledger" not in server_info:
        raise XRPLRequestFailureException(response.result)

    base_fee = server_info["validated_ledger"]["base_fee_xrp"]

    if "load_factor" not in server_info:
        load_factor = 1
    else:
        load_factor = server_info["load_factor"]

    fee = base_fee * load_factor
    # TODO: add cushion and max fee params to this method
    return "%.6f" % fee
