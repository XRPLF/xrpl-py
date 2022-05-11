"""Parse balance changes of every account involved in the given transaction."""

from __future__ import annotations

from typing import List

from pydash import flatten

from xrpl.models import TransactionMetadata
from xrpl.utils.txn_parser.utils import (
    BalanceChangesType,
    get_quantites,
    group_by_account,
    normalize_nodes,
)


def get_balance_changes(metadata: TransactionMetadata) -> List[BalanceChangesType]:
    """
    Parse all balance changes from a transaction's metadata.

    Args:
        metadata: Transactions metadata.

    Returns:
        All balance changes caused by a transaction.
        The balance changes are grouped by the affected account addresses.
    """
    quantities = map(lambda node: get_quantites(node), normalize_nodes(metadata))
    flattened_quantities = list(flatten(quantities))
    return group_by_account(flattened_quantities)
