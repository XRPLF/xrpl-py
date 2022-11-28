"""High-level methods that fetch transaction information from the XRP Ledger."""

import asyncio
from typing import Optional

from deprecated.sphinx import deprecated

from xrpl.asyncio.transaction import ledger
from xrpl.clients.sync_client import SyncClient
from xrpl.models.response import Response


@deprecated(
    reason="Sending a Tx request directly is just as easy to use.",
    version="1.8.0",
)
def get_transaction_from_hash(
    tx_hash: str,
    client: SyncClient,
    binary: bool = False,
    min_ledger: Optional[int] = None,
    max_ledger: Optional[int] = None,
) -> Response:
    """
    Given a transaction hash, fetch the corresponding transaction from the ledger.

    Args:
        tx_hash: the transaction hash.
        client: the network client used to communicate with a rippled node.
        binary: If true, return transaction data and metadata as binary
            serialized to hexadecimal strings. If false, return transaction data and
            metadata as JSON. The default is false.
        min_ledger: Use this with max_ledger to specify a range of up to
            1000 ledger indexes, starting with this ledger (inclusive). If the server
            cannot find the transaction, it confirms whether it was able to search all
            the ledgers in this range.
        max_ledger: Use this with min_ledger to specify a range of up to
            1000 ledger indexes, ending with this ledger (inclusive). If the server
            cannot find the transaction, it confirms whether it was able to search
            all the ledgers in the requested range.

    Returns:
        The Response object containing the transaction info.

    Raises:
        XRPLRequestFailureException: if the transaction fails.
    """
    return asyncio.run(
        ledger.get_transaction_from_hash(
            tx_hash,
            client,
            binary,
            min_ledger,
            max_ledger,
        )
    )
