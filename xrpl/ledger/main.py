"""High-level ledger methods with the XRPL ledger."""

from typing import Any, Dict, cast

from xrpl.clients import Client
from xrpl.models.requests import Fee, Ledger


def get_latest_validated_ledger_sequence(client: Client) -> int:
    """
    Returns the sequence number of the latest validated ledger.

    Args:
        client: The network client to use to send the request.

    Returns:
        The sequence number of the latest validated ledger.
    """
    response = client.request(Ledger(ledger_index="validated"))
    result = cast(Dict[str, Any], response.result)
    return cast(int, result["ledger_index"])


def get_fee(client: Client) -> str:
    """
    Query the ledger for the current minimum transaction fee.

    Args:
        client: the network client used to make network calls.

    Returns:
        The minimum fee for transactions.
    """
    response = client.request(Fee())
    result = cast(Dict[str, Any], response.result)
    return cast(str, result["drops"]["minimum_fee"])
