"""Utils for balance_changes."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Callable, Dict, List, Optional, Union, cast

from pydash import compact, flatten, group_by, map_, map_values  # type: ignore

from xrpl.utils.txn_parser.utils.transaction_data_utils import (
    AccountBalance,
    NormalizedFields,
    NormalizedNode,
)
from xrpl.utils.xrp_conversions import drops_to_xrp


@dataclass
class TrustLineQuantity:
    """Trust line quantity.

    Args:
        address (str):
            Accounts address.
        balance (AccountBalance):
            Accounts balance.
    """

    address: str
    balance: AccountBalance


def _parse_value(value: Union[AccountBalance, str]) -> Decimal:
    """Formats a balances value into a Decimal.

    Args:
        value (Union[AccountBalance, str]):
            Accounts balance.

    Returns:
        Decimal: Account balance value as Decimal.
    """
    if isinstance(value, AccountBalance):  # issued currency amount
        return Decimal(value.value)
    else:  # XRP amount
        return Decimal(value)


def parse_final_balance(node: NormalizedNode) -> Optional[Decimal]:
    """Parse final balance.

    Args:
        node (NormalizedNode):
            Normalized node.

    Returns:
        Optional[Decimal]:
            The balance value as Decimal.
    """
    if node.new_fields and hasattr(node.new_fields, "Balance"):
        new_balance = cast(Union[AccountBalance, str], node.new_fields.Balance)
        return _parse_value(value=new_balance)
    if node.final_fields and hasattr(node.final_fields, "Balance"):
        final_balance = cast(Union[AccountBalance, str], node.final_fields.Balance)
        return _parse_value(value=final_balance)

    return None


def compute_balance_changes(node: NormalizedNode) -> Optional[Decimal]:
    """Compute balance changes.

    Args:
        node (NormalizedNode):
            Normalized node.

    Returns:
        Optional[Decimal]:
            The parsed value.
    """
    value = None
    if isinstance(node.new_fields, NormalizedFields) and hasattr(
        node.new_fields, "Balance"
    ):
        new_balance = cast(Union[AccountBalance, str], node.new_fields.Balance)
        value = _parse_value(value=new_balance)
    if (
        node.previous_fields is not None
        and hasattr(node.previous_fields, "Balance")
        and node.final_fields is not None
        and hasattr(node.final_fields, "Balance")
    ):
        final_balance = cast(Union[AccountBalance, str], node.final_fields.Balance)
        previous_balance = cast(
            Union[AccountBalance, str], node.previous_fields.Balance
        )
        value = _parse_value(value=final_balance) - _parse_value(
            value=previous_balance,
        )

    if value and value != 0:
        return value
    else:
        return None


def _parse_xrp_quantity(
    node: NormalizedNode,
    value_parser: Callable[[NormalizedNode], Optional[Decimal]],
) -> Optional[TrustLineQuantity]:
    """Parse XRP quantity.

    Args:
        node (NormalizedNode):
            Normalized node.
        value_parser (Callable[[NormalizedNode], Optional[Decimal]]):
            Parser to get values needed.

    Returns:
        Optional[TrustLineQuantity]:
            Trust line quantity.
    """
    value = value_parser(node)
    if value is None:
        return None

    # determine if the XRP value is negative
    is_negative = False
    if str(value).startswith("-"):
        is_negative = True

    if node.final_fields is not None:
        address = cast(str, node.final_fields.Account)
    elif node.new_fields is not None:
        address = cast(str, node.new_fields.Account)
    else:
        address = ""

    result = TrustLineQuantity(
        address=address,
        balance=AccountBalance(
            counterparty="",
            currency="XRP",
            value=f"{drops_to_xrp(str(abs(int(value))))}"
            if not is_negative  # if XRP amount is positive
            else f"-{drops_to_xrp(str(abs(int(value))))}",  # if XRP is negative
        ),
    )

    return result


def _flip_trustline_perspective(quantity: TrustLineQuantity) -> TrustLineQuantity:
    """Flip the trust line perspective.

    Args:
        quantity (TrustLineQuantity):
            Trust line quantity.

    Returns:
        TrustLineQuantity:
            Flipped trust line quantity.
    """
    negated_balance = 0 - Decimal(quantity.balance.value)
    result = TrustLineQuantity(
        address=quantity.balance.counterparty,
        balance=AccountBalance(
            counterparty=quantity.address,
            currency=quantity.balance.currency,
            value=str(negated_balance),
        ),
    )

    return result


def _parse_trustline_quantity(
    node: NormalizedNode,
    value_parser: Callable[[NormalizedNode], Optional[Decimal]],
) -> Optional[List[TrustLineQuantity]]:
    """Parse trust line quantity.

    Args:
        node (NormalizedNode):
            Normalized node.
        value_parser (Callable[[NormalizedNode], Optional[Decimal]]):
            Parser to get values needed.

    Returns:
        Optional[List[TrustLineQuantity]]:
            Trust line quantity.
    """
    value = value_parser(node)
    if value is None:
        return None
    fields = node.final_fields if node.new_fields is None else node.new_fields

    if fields is None:
        return None

    assert (
        isinstance(fields.LowLimit, AccountBalance)
        and isinstance(fields.HighLimit, AccountBalance)
        and isinstance(fields.Balance, AccountBalance)
    )
    result = TrustLineQuantity(
        address=fields.LowLimit.counterparty,
        balance=AccountBalance(
            counterparty=fields.HighLimit.counterparty,
            currency=fields.Balance.currency,
            value=str(value),
        ),
    )

    return [result, _flip_trustline_perspective(quantity=result)]


def _group_by_address(
    balance_changes: List[TrustLineQuantity],
) -> Dict[str, List[AccountBalance]]:
    """Groups the balances changes by address.

    Args:
        balance_changes (List[TrustlineQuantity]):
            A dictionary of accounts balances grouped by addresses.

    Returns:
        Dict[str, AccountBalance]:
            A dictionary with all balance changes grouped by addresses.
    """
    grouped = group_by(balance_changes, lambda node: node.address)
    mapped_group = map_values(
        grouped, lambda group: map_(group, lambda node: node.balance)
    )

    return mapped_group  # type: ignore


def parse_quantities(
    nodes: List[NormalizedNode],
    value_parser: Callable[[NormalizedNode], Optional[Decimal]],
) -> Dict[str, List[AccountBalance]]:
    """Parse final balance.

    Args:
        nodes (List[NormalizedNode]):
            Normalized nodes.
        value_parser (Callable[[NormalizedNode], Optional[Decimal]]):
            Value parser.

    Returns:
        Dict[str, AccountBalance]: The grouped account balance changes.
    """
    values: List[Any] = []
    for node in nodes:
        if node.entry_type == "AccountRoot":
            values.append(
                _parse_xrp_quantity(node=node, value_parser=value_parser),
            )
        elif node.entry_type == "RippleState":
            values.append(
                _parse_trustline_quantity(node=node, value_parser=value_parser),
            )
        else:
            values.append([])

    return _group_by_address(compact(flatten(values)))
