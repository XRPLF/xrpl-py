"""Helper functions for `get_balance_changes`."""

from decimal import Decimal
from typing import List, Optional

from pydash import group_by

from xrpl.models.amounts.amount import Amount
from xrpl.models.amounts.issued_currency_amount import IssuedCurrencyAmount
from xrpl.utils.txn_parser.utils.nodes import NormalizedNode
from xrpl.utils.txn_parser.utils.types import (
    BalanceChangesType,
    BalanceChangeType,
    BalanceType,
)
from xrpl.utils.xrp_conversions import drops_to_xrp


def _get_value(balance: Amount) -> Decimal:
    if isinstance(balance, str):
        return Decimal(balance)
    return Decimal(balance["value"])


def _compute_balance_change(node: NormalizedNode) -> Optional[Decimal]:
    value: Optional[Decimal] = None
    if node.get("NewFields") is not None:
        if node["NewFields"].get("Balance") is not None:
            value = _get_value(node["NewFields"]["Balance"])
    elif node.get("PreviousFields") is not None and node.get("FinalFields") is not None:
        if (
            node["PreviousFields"].get("Balance") is not None
            and node["FinalFields"].get("Balance") is not None
        ):
            value = _get_value(node["FinalFields"]["Balance"]) - _get_value(
                node["PreviousFields"]["Balance"]
            )
    if value is None or value == Decimal(0):
        return None
    return value


def _get_xrp_quantity(node: NormalizedNode) -> Optional[BalanceChangeType]:
    value = _compute_balance_change(node)
    if value is None:
        return None
    value_is_negative = value < Decimal(0)
    value = drops_to_xrp(str(value.copy_abs()))
    if value_is_negative:
        value = Decimal(f"-{value}")
    return BalanceChangeType(
        account=node["FinalFields"]["Account"]
        if node.get("FinalFields") is not None
        else node["NewFields"]["Account"],
        balance=BalanceType(currency="XRP", value=f"{value.normalize():f}"),
    )


def _flip_trustline_perspective(balance_change: BalanceChangeType) -> BalanceChangeType:
    negated_balance = Decimal(balance_change["balance"]["value"]).copy_negate()
    return BalanceChangeType(
        account=balance_change["balance"]["issuer"],
        balance=BalanceType(
            currency=balance_change["balance"]["currency"],
            issuer=balance_change["account"],
            value=f"{negated_balance.normalize():f}",
        ),
    )


def _get_trustline_quantity(node: NormalizedNode) -> List[BalanceChangeType]:
    """
    Computes the complete list of every balance that changed in the ledger
    as a result of the given transaction.

    Args:
        node: The affected node.

    Returns:
        A list of balance changes.
    """
    value = _compute_balance_change(node)
    if value is None:
        return None
    fields = (
        node["NewFields"] if node.get("NewFields") is not None else node["FinalFields"]
    )

    result = BalanceChangeType(
        account=fields["LowLimit"]["issuer"],
        balance=BalanceType(
            currency=IssuedCurrencyAmount(**fields["Balance"]).currency,
            issuer=fields["HighLimit"]["issuer"],
            value=f"{value.normalize():f}",
        ),
    )
    return [result, _flip_trustline_perspective(result)]


def get_quantites(node: NormalizedNode) -> List[BalanceChangeType]:
    """
    Retreive the balance changes from a node.

    Args:
        node: The affected node.

    Returns:
        A list of balance changes.
    """
    if node["LedgerEntryType"] == "AccountRoot":
        xrp_quantity = _get_xrp_quantity(node)
        if xrp_quantity is None:
            return []
        return [xrp_quantity]
    if node["LedgerEntryType"] == "RippleState":
        trustline_quantity = _get_trustline_quantity(node)
        if trustline_quantity is None:
            return []
        return trustline_quantity
    return []


def group_by_account(
    balance_changes: List[BalanceChangeType],
) -> List[BalanceChangesType]:
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
        balance_changes_object = BalanceChangesType(
            account=account,
            balances=[],
        )
        for balance in balances:
            balance.pop("account")
            balance_changes_object["balances"].append(list(balance.values())[0])
        result.append(balance_changes_object)
    return result
