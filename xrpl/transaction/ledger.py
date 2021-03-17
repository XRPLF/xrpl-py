"""High-level methods that fetch transaction information from the XRP Ledger."""

from xrpl.clients import Client
from xrpl.models.requests import Tx
from xrpl.models.response import Response


def get_transaction_from_hash(tx_hash: str, client: Client) -> Response:
    """
    Given a transaction hash, fetch the corresponding transaction from the ledger.

    Args:
        tx_hash: the transaction hash.
        client: the network client used to communicate with a rippled node.

    Returns:
        The Response object containing the transaction info.
    """
    response = client.request(Tx(transaction=tx_hash))
    return response
