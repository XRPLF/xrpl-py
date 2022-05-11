"""Parse balance changes of every account involved in the given transaction."""

from decimal import Decimal
from typing import List, Optional, Union

from pydash import flatten  # type: ignore

from xrpl.models import TransactionMetadata
from xrpl.utils.txn_parser.utils import (
    BalanceChanges,
    get_quantities,
    group_by_account,
    normalize_nodes,
)
from xrpl.utils.txn_parser.utils.nodes import NormalizedNode
from xrpl.utils.txn_parser.utils.types import Balance


def _get_value(balance: Union[Balance, str]) -> Decimal:
    if isinstance(balance, str):
        return Decimal(balance)
    return Decimal(balance["value"])


def _compute_balance_change(node: NormalizedNode) -> Optional[Decimal]:
    """
    Get the balance change from a node.

    Args:
        node: The affected node.

    Returns:
        The balance change.
    """
    value: Optional[Decimal] = None
    if node.get("NewFields") is not None:
        assert node["NewFields"] is not None
        if node["NewFields"].get("Balance"):
            assert node["NewFields"]["Balance"] is not None
            value = _get_value(node["NewFields"]["Balance"])
    elif node.get("PreviousFields") is not None and node.get("FinalFields") is not None:
        assert node["PreviousFields"] is not None and node["FinalFields"] is not None
        if (
            node["PreviousFields"].get("Balance") is not None
            and node["FinalFields"].get("Balance") is not None
        ):
            assert (
                node["PreviousFields"]["Balance"] is not None
                and node["FinalFields"]["Balance"] is not None
            )
            value = _get_value(node["FinalFields"]["Balance"]) - _get_value(
                node["PreviousFields"]["Balance"]
            )
    if value is None or value == Decimal(0):
        return None
    return value


def get_balance_changes(metadata: TransactionMetadata) -> List[BalanceChanges]:
    """
    Parse all balance changes from a transaction's metadata.

    Args:
        metadata: Transactions metadata.

    Returns:
        All balance changes caused by a transaction.
        The balance changes are grouped by the affected account addresses.
    """
    quantities = [
        get_quantities(node, _compute_balance_change)
        for node in normalize_nodes(metadata)
    ]
    flattened_quantities = list(flatten(quantities))
    return group_by_account(flattened_quantities)
