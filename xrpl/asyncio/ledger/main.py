"""High-level ledger methods with the XRPL ledger."""

from typing import Optional, cast

from xrpl.asyncio.clients import Client, XRPLRequestFailureException
from xrpl.asyncio.ledger.utils import calculate_fee_dynamically
from xrpl.constants import XRPLException
from xrpl.models.requests import Fee, Ledger
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
    response = await client._request_impl(Ledger(ledger_index="validated"))
    if response.is_successful():
        return cast(int, response.result["ledger_index"])

    raise XRPLRequestFailureException(response.result)


async def get_latest_open_ledger_sequence(client: Client) -> int:
    """
    Returns the sequence number of the latest open ledger.

    Note: While specifying ledgers in the Ledger RPC call, the appropriate ledger_index
    is "current", not "open". However, this method signature is retained as-is for
    backwards compatibility.

    Read this document for more info:
    https://xrpl.org/docs/references/http-websocket-apis/public-api-methods/ledger-methods/ledger#request-format

    Args:
        client: The network client to use to send the request.

    Returns:
        The sequence number of the latest open ledger.

    Raises:
        XRPLRequestFailureException: if the rippled API call fails.
    """
    response = await client._request_impl(Ledger(ledger_index="current"))

    if response.is_successful():
        # validate that the `current` ledger is retrieved
        if response.result["ledger"]["closed"] is True:
            raise XRPLException("`closed` key found while requesting current ledger")
        if response.result["validated"] is True:
            raise XRPLException("`validated` key found while requesting current ledger")
        if "ledger_index" in response.result:
            raise XRPLException("`ledger_index` key is not relevant in current ledger")
        if "ledger_current_index" not in response.result:
            raise XRPLException(
                "`ledger_current_index` key must be present in current ledger"
            )

        return cast(int, response.result["ledger_current_index"])

    raise XRPLRequestFailureException(response.result)


async def get_fee(
    client: Client, *, max_fee: Optional[float] = 2, fee_type: str = "open"
) -> str:
    """
    Query the ledger for the current transaction fee.

    Args:
        client: the network client used to make network calls.
        max_fee: The maximum fee in XRP that the user wants to pay. If load gets too
            high, then the fees will not scale past the maximum fee. If None, there is
            no ceiling for the fee. The default is 2 XRP.
        fee_type: The type of fee to return. The options are "open" (the load-scaled
            fee to get into the open ledger), "minimum" (the minimum transaction
            fee) or "dynamic" (dynamic fee-calculation based on the queue size
            of the node). The default is "open". The recommended option is
            "dynamic".

    Returns:
        The transaction fee, in drops.
        `Read more about drops <https://xrpl.org/currency-formats.html#xrp-amounts>`_

    Raises:
        XRPLException: if an incorrect option for `fee_type` is passed in.
        XRPLRequestFailureException: if the rippled API call fails.
    """
    response = await client._request_impl(Fee())
    if not response.is_successful():
        raise XRPLRequestFailureException(response.result)

    result = response.result
    drops = result["drops"]
    if fee_type == "open":
        fee = cast(str, drops["open_ledger_fee"])
    elif fee_type == "minimum":
        fee = cast(str, drops["minimum_fee"])
    elif fee_type == "dynamic":
        fee = calculate_fee_dynamically(fee_data_set=result)
    else:
        raise XRPLException(
            '`fee_type` param must be "open", "minimum" or "dynamic".'
            f" {fee_type} is not a valid option."
        )
    if max_fee is not None:
        max_fee_drops = int(xrp_to_drops(max_fee))
        if max_fee_drops < int(fee):
            fee = str(max_fee_drops)
    return fee
