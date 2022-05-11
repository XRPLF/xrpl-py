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
    final_fields = node.get("FinalFields")
    new_fields = node.get("NewFields")
    if final_fields is not None:
        account = final_fields.get("Account")
        if account is not None:
            return BalanceChange(
                account=account,
                balance=Balance(  # type: ignore
                    currency="XRP",
                    value=f"{value.normalize():f}",
                ),
            )
    if new_fields is not None:
        account = new_fields.get("Account")
        if account is not None:
            return BalanceChange(
                account=account,
                balance=Balance(  # type: ignore
                    currency="XRP",
                    value=f"{value.normalize():f}",
                ),
            )
    return None


def _flip_trustline_perspective(balance_change: BalanceChange) -> BalanceChange:
    negated_balance = Decimal(balance_change["balance"]["value"]).copy_negate()
    balance = balance_change.get("balance")
    assert balance is not None
    issuer = balance.get("issuer")
    assert issuer is not None
    return BalanceChange(
        account=issuer,
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
    assert fields is not None
    low_limit = fields.get("LowLimit")
    balance = fields.get("Balance")
    high_limit = fields.get("HighLimit")
    if low_limit is not None and balance is not None and high_limit is not None:
        low_limit_issuer = low_limit.get("issuer")
        assert isinstance(balance, dict)
        balance_currency = balance.get("currency")
        high_limit_issuer = high_limit.get("issuer")
        if (
            low_limit_issuer is not None
            and balance_currency is not None
            and high_limit_issuer is not None
        ):
            result = BalanceChange(
                account=low_limit_issuer,
                balance=Balance(
                    currency=balance_currency,
                    issuer=high_limit_issuer,
                    value=f"{value.normalize():f}",
                ),
            )
            return [result, _flip_trustline_perspective(result)]
    return None


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
