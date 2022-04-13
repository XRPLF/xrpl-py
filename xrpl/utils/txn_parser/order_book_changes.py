"""Parse order book changes caused by a transaction."""
from __future__ import annotations

from typing import Any, Dict, Union, cast

from xrpl.utils.txn_parser.utils import (
    RawTxnType,
    SubscriptionRawTxnType,
    compute_order_book_changes,
    group_by_address_order_book,
    normalize_nodes,
    normalize_transaction,
    validate_transaction_fields,
)


def parse_order_book_changes(
    transaction: Union[RawTxnType, SubscriptionRawTxnType],
) -> Dict[str, Any]:
    """Parse all order book changes that were caused by a transaction.

    Args:
        transaction (Union[RawTxnType, SubscriptionRawTxnType]):
            Raw transaction data including the account that
            sent the transaction and the affected nodes.

    Returns:
        Dict[str, Any]:
            Order book changes.
    """
    validate_transaction_fields(transaction_data=transaction)
    if "transaction" in transaction:
        transaction = cast(SubscriptionRawTxnType, transaction)
        transaction = normalize_transaction(transaction_data=transaction)

    nodes = normalize_nodes(transaction_data=transaction)
    order_changes = compute_order_book_changes(nodes=nodes)

    if order_changes:
        result = group_by_address_order_book(order_changes)
    else:
        result = {}

    return result
