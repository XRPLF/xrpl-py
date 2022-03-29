"""
Parse balance changes, final balances and previous balances of every
account involved in the given transaction.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Dict, List, Union

from xrpl.utils.tx_parser.utils import (
    METADATA_TYPE,
    SUBSCRIPTION_METADATA_TYPE,
    compute_balance_changes,
    is_valid_metadata,
    normalize_metadata,
    normalize_nodes,
    parse_final_balance,
    parse_quantities,
)


def parse_previous_balances(
    metadata: Union[METADATA_TYPE, SUBSCRIPTION_METADATA_TYPE],
) -> Dict[str, List[Dict[str, str]]]:
    """Parse the previous balances of all accounts affected
    by the transaction before it occurred.

    Args:
        metadata (Union[METADATA_TYPE, SUBSCRIPTION_METADATA_TYPE]):
            Transaction metadata including the account that
            sent the transaction and the affected nodes.

    Returns:
        Dict[str, List[Dict[str, str]]]:
            All previous balances.
    """
    is_valid_metadata(metadata=metadata)
    if "transaction" in metadata:
        metadata = normalize_metadata(metadata=metadata)

    balance_changes = parse_balance_changes(metadata=metadata)
    final_balances = parse_final_balances(metadata=metadata)

    for account, balances in balance_changes.items():
        for count, balance in enumerate(balances):
            final_balances_value = final_balances[account][count]["Value"]
            final_balances[account][count]["Value"] = str(
                Decimal(final_balances_value) - Decimal(balance["Value"])
            )

    return final_balances


def parse_balance_changes(
    metadata: Union[METADATA_TYPE, SUBSCRIPTION_METADATA_TYPE],
) -> Dict[str, List[Dict[str, str]]]:
    """Parse the balance changes of all accounts affected
    by the transaction after it occurred.

    Args:
        metadata (Union[METADATA_TYPE, SUBSCRIPTION_METADATA_TYPE]):
            Transaction metadata including the account that
            sent the transaction and the affected nodes.

    Returns:
        Dict[str, List[Dict[str, str]]]:
            All balance changes.
    """
    is_valid_metadata(metadata=metadata)
    if "transaction" in metadata:
        metadata = normalize_metadata(metadata=metadata)

    nodes = normalize_nodes(metadata=metadata)
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
    metadata: Union[METADATA_TYPE, SUBSCRIPTION_METADATA_TYPE],
) -> Dict[str, List[Dict[str, str]]]:
    """Parse the final balances of all accounts affected
    by the transaction after it occurred.

    Args:
        metadata (Union[METADATA_TYPE, SUBSCRIPTION_METADATA_TYPE]):
            Transaction metadata including the account that
            sent the transaction and the affected nodes.

    Returns:
        Dict[str, List[Dict[str, str]]]:
            All final balances.
    """
    is_valid_metadata(metadata=metadata)
    if "transaction" in metadata:
        metadata = normalize_metadata(metadata=metadata)

    nodes = normalize_nodes(metadata=metadata)
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
