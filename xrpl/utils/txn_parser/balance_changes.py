"""
Parse balance changes, final balances and previous balances of every
account involved in the given transaction.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List, Union, cast

from xrpl.utils.txn_parser.utils import (
    RawTxnType,
    SubscriptionRawTxnType,
    compute_balance_changes,
    normalize_nodes,
    normalize_transaction,
    parse_final_balance,
    parse_quantities,
    validate_transaction_fields,
)


def parse_previous_balances(
    transaction: Union[RawTxnType, SubscriptionRawTxnType],
) -> Dict[str, Any]:
    """Parse the previous balances of all accounts affected
    by the transaction before it occurred.

    Args:
        transaction (Union[RawTxnType, SubscriptionRawTxnType]):
            Raw transaction data including the account that
            sent the transaction and the affected nodes.

    Returns:
        Dict[str, Any]:
            All previous balances.
    """
    validate_transaction_fields(transaction_data=transaction)
    if "transaction" in transaction:
        transaction = cast(SubscriptionRawTxnType, transaction)
        transaction = normalize_transaction(transaction_data=transaction)

    balance_changes = parse_balance_changes(transaction=transaction)
    final_balances = parse_final_balances(transaction=transaction)

    for account, balances in balance_changes.items():
        for count, balance in enumerate(balances):
            final_balances_value = final_balances[account][count]["Value"]
            final_balances[account][count]["Value"] = str(
                Decimal(final_balances_value) - Decimal(balance["Value"])
            )

    return final_balances


def parse_balance_changes(
    transaction: Union[RawTxnType, SubscriptionRawTxnType],
) -> Dict[str, Any]:
    """Parse the balance changes of all accounts affected
    by the transaction after it occurred.

    Args:
        transaction (Union[RawTxnType, SubscriptionRawTxnType]):
            Raw transaction data including the account that
            sent the transaction and the affected nodes.

    Returns:
        Dict[str, Any]:
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
            if isinstance(obj.counterparty, tuple):
                obj.counterparty = obj.counterparty[0]
            result[address].append(
                {
                    "Counterparty": obj.counterparty,
                    "Currency": obj.currency,
                    "Value": obj.value,
                }
            )

    return result


def parse_final_balances(
    transaction: Union[RawTxnType, SubscriptionRawTxnType],
) -> Dict[str, Any]:
    """Parse the final balances of all accounts affected
    by the transaction after it occurred.

    Args:
        transaction (Union[RawTxnType, SubscriptionRawTxnType]):
            Raw transaction data including the account that
            sent the transaction and the affected nodes.

    Returns:
        Dict[str, Any]:
            All final balances.
    """
    validate_transaction_fields(transaction_data=transaction)
    if "transaction" in transaction:
        transaction = cast(SubscriptionRawTxnType, transaction)
        transaction = normalize_transaction(transaction_data=transaction)

    nodes = normalize_nodes(transaction_data=transaction)
    parsed_quantities = parse_quantities(
        nodes=nodes,
        value_parser=parse_final_balance,
    )

    result: Dict[str, List[Dict[str, str]]] = {}
    for address, change in parsed_quantities.items():
        result[address] = []
        for obj in change:
            if isinstance(obj.counterparty, tuple):
                obj.counterparty = obj.counterparty[0]
            result[address].append(
                {
                    "Counterparty": obj.counterparty,
                    "Currency": obj.currency,
                    "Value": obj.value,
                }
            )

    return result
