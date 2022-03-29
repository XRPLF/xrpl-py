"""Parse order book changes caused by a transaction."""
from __future__ import annotations

from typing import Dict, List, Union

from xrpl.utils.tx_parser.utils import (
    METADATA_TYPE,
    SUBSCRIPTION_METADATA_TYPE,
    compute_order_book_changes,
    group_by_address_order_book,
    is_valid_metadata,
    normalize_metadata,
    normalize_nodes,
)


def parse_order_book_changes(
    metadata: Union[METADATA_TYPE, SUBSCRIPTION_METADATA_TYPE],
) -> Dict[
    str,
    List[Dict[str, Union[Dict[str, Union[Dict[str, str], str]], str, int, bool]]],
]:
    """Parse all order book changes that were caused by a transaction.

    Args:
        metadata (Union[METADATA_TYPE, SUBSCRIPTION_METADATA_TYPE]):
            Transaction metadata including the account that
            sent the transaction and the affected nodes.

    Returns:
        Dict[str, List[Dict[str, Union[Dict[str, Union[
        Dict[str, str], str]], str, int, bool]]]]:
            Order book changes.
    """
    is_valid_metadata(metadata=metadata)
    if "transaction" in metadata:
        metadata = normalize_metadata(metadata)

    nodes = normalize_nodes(metadata=metadata)
    order_changes = compute_order_book_changes(nodes=nodes)

    if order_changes:
        result = group_by_address_order_book(order_changes)
    else:
        result = {}

    return result
