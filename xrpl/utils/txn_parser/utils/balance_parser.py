"""Helper functions for balance parser."""

from decimal import Decimal
from typing import Dict, List, Optional, Union

from xrpl.utils.txn_parser.utils.nodes import NormalizedNode
from xrpl.utils.txn_parser.utils.types import Balance, ComputedBalance, ComputedBalances
from xrpl.utils.xrp_conversions import drops_to_xrp


def _get_xrp_quantity(
    node: NormalizedNode,
    value: Optional[Decimal],
) -> Optional[ComputedBalance]:
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
            return ComputedBalance(
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
            return ComputedBalance(
                account=account,
                balance=Balance(
                    currency="XRP",
                    value=f"{xrp_value.normalize():f}",
                ),
            )
    return None


def _flip_trustline_perspective(computed_balance: ComputedBalance) -> ComputedBalance:
    balance = computed_balance["balance"]
    negated_value = Decimal(balance["value"]).copy_negate()
    issuer = balance["issuer"]
    return ComputedBalance(
        account=issuer,
        balance=Balance(
            currency=balance["currency"],
            issuer=computed_balance["account"],
            value=f"{negated_value.normalize():f}",
        ),
    )


def _get_trustline_quantity(
    node: NormalizedNode,
    value: Optional[Decimal],
) -> List[ComputedBalance]:
    """
    Computes the complete list of every balance affected by the transaction.

    Args:
        node: The affected node.
        value: The currency amount value.

    Returns:
        A list of computed balances.
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
            result = ComputedBalance(
                account=low_limit_issuer,
                balance=Balance(
                    currency=balance_currency,
                    issuer=high_limit_issuer,
                    value=f"{value.normalize():f}",
                ),
            )
            return [result, _flip_trustline_perspective(result)]
    return []


def _group_balance(
    computed_balances: List[ComputedBalance],
) -> Dict[str, List[ComputedBalance]]:
    grouped_balances: Dict[str, List[ComputedBalance]] = {}
    for balance in computed_balances:
        account = balance["account"]
        if account not in grouped_balances:
            grouped_balances[account] = []
        grouped_balances[account].append(balance)
    return grouped_balances


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


def get_node_balance(
    node: NormalizedNode,
    value: Optional[Decimal],
) -> List[ComputedBalance]:
    """
    Retrieve the balance from a node.

    Args:
        node: The affected node.
        value: The currency amount's value

    Returns:
        A list of balances.
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
    computed_balance: List[ComputedBalance],
) -> List[ComputedBalances]:
    """
    Groups the computed balances in one list for each account.

    Args:
        computed_balance: All computed balances cause by a transaction.

    Returns:
        The grouped computed balances.
    """
    grouped = _group_balance(computed_balance)
    result = []
    for account, account_balances in grouped.items():
        balances: List[Balance] = []
        for balance in account_balances:
            balances.append(balance["balance"])
        result.append(
            ComputedBalances(
                account=account,
                balances=balances,
            )
        )
    return result
