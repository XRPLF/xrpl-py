"""Parse balance changes of every account involved in the given transaction."""

from typing import Any, Dict, List, Union, cast

from xrpl.utils.txn_parser.utils import (
    RawTxnType,
    SubscriptionRawTxnType,
    compute_balance_changes,
    normalize_nodes,
    normalize_transaction,
    parse_quantities,
    validate_transaction_fields,
)


def parse_balance_changes(
    transaction: Union[RawTxnType, SubscriptionRawTxnType],
) -> Dict[str, Any]:
    """
    Parse the balance changes of all accounts affected
    by the transaction after it occurred.

    Args:
        transaction: Raw transaction data including the account that
            sent the transaction and the metadata.

    Returns:
        All balance changes.
    """
    validate_transaction_fields(transaction_data=transaction)
    if "transaction" in transaction:
        transaction = cast(SubscriptionRawTxnType, transaction)
        transaction = normalize_transaction(transaction_data=transaction)
    nodes = normalize_nodes(transaction_data=transaction)
    parsedQuantities = parse_quantities(
        nodes=nodes, value_parser=compute_balance_changes
    )
    result: Dict[str, List[Dict[str, str]]] = {}
    for address, change in parsedQuantities.items():
        result[address] = []
        for obj in change:
            if isinstance(obj.issuer, tuple):
                obj.issuer = obj.issuer[0]
            result[address].append(
                {
                    "issuer": obj.issuer,
                    "currency": obj.currency,
                    "value": obj.value,
                }
            )
    return result
