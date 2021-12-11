"""High-level ledger methods with the XRPL ledger."""

from typing import Optional, cast

from xrpl.asyncio.clients import Client, XRPLRequestFailureException
from xrpl.models.requests import Ledger, ServerInfo
from xrpl.utils import xrp_to_drops


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


async def get_fee(client: Client, max_fee: Optional[float] = 2) -> str:
    """
    Query the ledger for the current minimum transaction fee.

    Args:
        client: the network client used to make network calls.
        max_fee: The maximum fee in XRP that the user wants to pay. If load gets too
            high, then the fees will not scale past the maximum fee. If None, there is
            no ceiling for the fee. The default is 2 XRP.

    Returns:
        The load-scaled transaction cost, in drops.

    Raises:
        XRPLRequestFailureException: if the rippled API call fails.
    """
    response = await client.request_impl(ServerInfo())
    if not response.is_successful():
        raise XRPLRequestFailureException(response.result)

    server_info = response.result["info"]
    if "validated_ledger" not in server_info:
        raise XRPLRequestFailureException(response.result)

    base_fee = int(xrp_to_drops(server_info["validated_ledger"]["base_fee_xrp"]))

    if "load_factor" not in server_info:
        load_factor = 1
    else:
        load_factor = server_info["load_factor"]

    fee = base_fee * load_factor
    if max_fee is not None:
        max_fee_drops = int(xrp_to_drops(max_fee))
        if max_fee_drops < fee:
            fee = max_fee_drops
    # TODO: add cushion param to this method
    # rounds to the nearest integer, then converts to string
    return str(int(fee))
