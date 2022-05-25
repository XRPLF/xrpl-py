"""Helper functions for balance parser."""

from decimal import Decimal
from typing import Dict, List, Optional, Union

from xrpl.utils.txn_parser.utils.nodes import NormalizedNode
from xrpl.utils.txn_parser.utils.types import Balance, BalanceChange, BalanceChanges
from xrpl.utils.xrp_conversions import drops_to_xrp


def _get_xrp_quantity(
    node: NormalizedNode,
    value: Optional[Decimal],
) -> Optional[BalanceChange]:
    if value is None:
        return None
    absolute_value = value.copy_abs()
    xrp_value = (
        drops_to_xrp(str(absolute_value)).copy_negate()
        if value.is_signed()
        else drops_to_xrp(str(absolute_value))
    )
    final_fields = node.get("FinalFields")
    if final_fields is not None:
        account = final_fields.get("Account")
        if account is not None:
            return BalanceChange(
                account=account,
                balance=Balance(
                    currency="XRP",
                    value=f"{xrp_value.normalize():f}",
                ),
            )
    new_fields = node.get("NewFields")
    if new_fields is not None:
        account = new_fields.get("Account")
        if account is not None:
            return BalanceChange(
                account=account,
                balance=Balance(
                    currency="XRP",
                    value=f"{xrp_value.normalize():f}",
                ),
            )
    return None


def _flip_trustline_perspective(balance_change: BalanceChange) -> BalanceChange:
    balance = balance_change["balance"]
    negated_value = Decimal(balance["value"]).copy_negate()
    issuer = balance["issuer"]
    return BalanceChange(
        account=issuer,
        balance=Balance(
            currency=balance["currency"],
            issuer=balance_change["account"],
            value=f"{negated_value.normalize():f}",
        ),
    )


def _get_trustline_quantity(
    node: NormalizedNode,
    value: Optional[Decimal],
) -> List[BalanceChange]:
    """
    Computes the complete list of every balance that changed in the ledger
    as a result of the given transaction.

    Args:
        node: The affected node.
        value: The currency amount value.

    Returns:
        A list of balance changes.
    """
    if value is None:
        return []
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
    return []


def _group_balance_changes(
    balance_changes: List[BalanceChange],
) -> Dict[str, List[BalanceChange]]:
    grouped_balance_changes: Dict[str, List[BalanceChange]] = {}
    for change in balance_changes:
        account = change["account"]
        if account not in grouped_balance_changes:
            grouped_balance_changes[account] = []
        grouped_balance_changes[account].append(change)
    return grouped_balance_changes


def get_value(balance: Union[Dict[str, str], str]) -> Decimal:
    """
    Get a currency amount's value.

    Args:
        balance: Account's balance.

    Returns:
        The currency amount's value.
    """
    if isinstance(balance, str):
        return Decimal(balance)
    return Decimal(balance["value"])


def get_node_balance_changes(
    node: NormalizedNode,
    value: Optional[Decimal],
) -> List[BalanceChange]:
    """
    Retrieve the balance changes from a node.

    Args:
        node: The affected node.
        value: The currency amount's value

    Returns:
        A list of balance changes.
    """
    if node["LedgerEntryType"] == "AccountRoot":
        xrp_quantity = _get_xrp_quantity(node, value)
        if xrp_quantity is None:
            return []
        return [xrp_quantity]
    if node["LedgerEntryType"] == "RippleState":
        trustline_quantity = _get_trustline_quantity(node, value)
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
    grouped = _group_balance_changes(balance_changes)
    result = []
    for account, account_balances in grouped.items():
        balances: List[Balance] = []
        for balance in account_balances:
            balances.append(balance["balance"])
        result.append(
            BalanceChanges(
                account=account,
                balances=balances,
            )
        )
    return result
