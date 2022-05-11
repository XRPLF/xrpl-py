"""Helper functions for balance parser."""

from decimal import Decimal
from typing import Callable, List, Optional

from pydash import group_by  # type: ignore

from xrpl.utils.txn_parser.utils.nodes import NormalizedNode
from xrpl.utils.txn_parser.utils.types import Balance, BalanceChange, BalanceChanges
from xrpl.utils.xrp_conversions import drops_to_xrp


def _get_xrp_quantity(
    node: NormalizedNode,
    value_parser: Callable[[NormalizedNode], Optional[Decimal]],
) -> Optional[BalanceChange]:
    value = value_parser(node)
    if value is None:
        return None
    value_is_negative = value < Decimal(0)
    value = drops_to_xrp(str(value.copy_abs()))
    if value_is_negative:
        value = Decimal(f"-{value}")
    return BalanceChange(
        account=node["FinalFields"]["Account"]  # type: ignore
        if node.get("FinalFields") is not None
        else node["NewFields"]["Account"],  # type: ignore
        balance=Balance(  # type: ignore
            currency="XRP",
            value=f"{value.normalize():f}",
        ),
    )


def _flip_trustline_perspective(balance_change: BalanceChange) -> BalanceChange:
    negated_balance = Decimal(balance_change["balance"]["value"]).copy_negate()
    return BalanceChange(
        account=balance_change["balance"]["issuer"],  # type: ignore
        balance=Balance(
            currency=balance_change["balance"]["currency"],
            issuer=balance_change["account"],
            value=f"{negated_balance.normalize():f}",
        ),
    )


def _get_trustline_quantity(
    node: NormalizedNode,
    value_parser: Callable[[NormalizedNode], Optional[Decimal]],
) -> Optional[List[BalanceChange]]:
    """
    Computes the complete list of every balance that changed in the ledger
    as a result of the given transaction.

    Args:
        node: The affected node.

    Returns:
        A list of balance changes.
    """
    value = value_parser(node)
    if value is None:
        return None
    fields = (
        node["NewFields"] if node.get("NewFields") is not None else node["FinalFields"]
    )

    result = BalanceChange(
        account=fields["LowLimit"]["issuer"],  # type: ignore
        balance=Balance(
            currency=fields["Balance"]["currency"],  # type: ignore
            issuer=fields["HighLimit"]["issuer"],  # type: ignore
            value=f"{value.normalize():f}",
        ),
    )
    return [result, _flip_trustline_perspective(result)]


def get_quantities(
    node: NormalizedNode,
    value_parser: Callable[[NormalizedNode], Optional[Decimal]],
) -> List[BalanceChange]:
    """
    Retrieve the balance changes from a node.

    Args:
        node: The affected node.
        value_parser: The needed value parser.

    Returns:
        A list of balance changes.
    """
    if node["LedgerEntryType"] == "AccountRoot":
        xrp_quantity = _get_xrp_quantity(node, value_parser)
        if xrp_quantity is None:
            return []
        return [xrp_quantity]
    if node["LedgerEntryType"] == "RippleState":
        trustline_quantity = _get_trustline_quantity(node, value_parser)
        if trustline_quantity is None:
            return []
        return trustline_quantity
    return []


def group_by_account(
    balance_changes: List[BalanceChange],
) -> List[BalanceChanges]:
    """
    Groups the balance changes in one list for each account.

    Args:
        balance_changes: All balance changes cause by a transaction.

    Returns:
        The grouped balance changes.
    """
    grouped = group_by(balance_changes, lambda change: change["account"])
    result = []
    for account, balances in grouped.items():
        balance_changes_object = BalanceChanges(
            account=account,
            balances=[],
        )
        for balance in balances:
            balance.pop("account")
            balance_changes_object["balances"].append(list(balance.values())[0])
        result.append(balance_changes_object)
    return result
