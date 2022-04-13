"""Utils for order_book_changes."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Union, cast

from pydash import filter_, group_by, map_  # type: ignore
from typing_extensions import Literal

from xrpl.utils.txn_parser.utils.transaction_data_utils import (
    AccountBalance,
    NormalizedNode,
)
from xrpl.utils.txn_parser.utils.types import CURRENCY_AMOUNT_TYPE
from xrpl.utils.xrp_conversions import drops_to_xrp

LFS_SELL = 0x00020000


@dataclass
class OrderChange:
    """Order change."""

    taker_pays: CURRENCY_AMOUNT_TYPE
    """TakerPays amount"""
    taker_gets: CURRENCY_AMOUNT_TYPE
    """TakerGets amount"""
    sell: bool
    """If flag 'sell' is set"""
    sequence: int
    """Sequence number"""
    status: Optional[
        Union[
            Literal["created"],
            Literal["partially-filled"],
            Literal["filled"],
            Literal["cancelled"],
        ]
    ]
    """Status of the offer"""
    quality: str
    """Offer quality"""
    expiration: Optional[Union[int, str]] = None
    """Expiration"""
    direction: Optional[str] = None
    """Buy or Sell."""
    total_received: Optional[CURRENCY_AMOUNT_TYPE] = None
    """Amount received"""
    total_paid: Optional[CURRENCY_AMOUNT_TYPE] = None
    """Amount paid"""
    account: Optional[str] = None
    """Accounts address"""


class ChangeAmount:
    """Amount changed by transaction."""

    def __init__(
        self: ChangeAmount,
        final_amount: Dict[str, str],
        previous_value: str,
    ) -> None:
        """
        Args:
            final_amount (Dict[str, str]): Final amount
            previous_value (str): Difference to Previous amount
        """
        self.final_amount = final_amount
        self.previous_value = previous_value


def group_by_address_order_book(
    order_changes: List[Dict[str, Union[Dict[str, str], bool, int, str]]]
) -> Dict[
    str,
    List[Dict[str, Union[Dict[str, Union[Dict[str, str], str]], str, int, bool]]],
]:
    """Group order book changes by addresses.

    Args:
        order_changes (List[Dict[str, Union[Dict[str, str], bool, int, str]]]):
            Order book changes

    Returns:
        Dict[str, Union[Dict[str, Union[Dict[str, str], str]], str, int, bool]]:
            Order book changes grouped by addresses.
    """
    return group_by(order_changes, lambda change: change["account"])  # type: ignore


def _parse_currency_amount(
    currency_amount: Union[str, AccountBalance]
) -> AccountBalance:
    """Parses an accounts balance and formats it into a standard format.

    Args:
        currency_amount (Union[str, AccountBalance]):
            Currency amount.

    Returns:
        AccountBalance: Account balance.
    """
    if isinstance(currency_amount, str):
        return AccountBalance(
            currency="XRP", counterparty="", value=str(drops_to_xrp(currency_amount))
        )

    return AccountBalance(
        currency=currency_amount.currency,
        counterparty=currency_amount.counterparty,
        value=str(currency_amount.value),
    )


def _calculate_delta(
    final_amount: Optional[AccountBalance],
    previous_amount: Optional[AccountBalance],
) -> Union[Decimal, int]:
    if isinstance(final_amount, AccountBalance) and isinstance(
        previous_amount, AccountBalance
    ):
        previous_value = Decimal(previous_amount.value)
        return 0 - previous_value

    return 0


def _parse_order_status(
    node: NormalizedNode,
) -> Optional[Literal["created", "partially-filled", "filled", "cancelled"]]:
    """Parses the status of an order.

    Returns:
        Optional[Literal['created', 'partially-filled', 'filled', 'cancelled']]:
            The order status.
    """
    if node.diff_type == "CreatedNode":
        return "created"

    if node.diff_type == "ModifiedNode":
        return "partially-filled"

    if node.diff_type == "DeletedNode":
        if hasattr(node, "previous_fields") and hasattr(
            node.previous_fields, "TakerPays"
        ):
            return "filled"
        return "cancelled"

    return None


def _parse_change_amount(
    node: NormalizedNode, side: Literal["TakerPays", "TakerGets"]
) -> Optional[Union[AccountBalance, ChangeAmount]]:
    """Parse the changed amount of an order.

    Args:
        node (NormalizedNode):
            Normalized node.
        side (Literal['TakerPays', 'TakerGets']):
            Side of the order to parse.

    Returns:
        Optional[Union[AccountBalance, ChangeAmount]]:
            The changed currency amount.
    """
    status = _parse_order_status(node=node)

    if status == "cancelled":
        return (
            _parse_currency_amount(currency_amount=getattr(node.final_fields, side))
            if (hasattr(node.final_fields, side))
            else None
        )
    if status == "created":
        return (
            _parse_currency_amount(currency_amount=getattr(node.new_fields, side))
            if (hasattr(node.new_fields, side))
            else None
        )

    # Else it has modified an offer.
    # Status is 'partially-filled' or 'filled'.
    final_amount = (
        _parse_currency_amount(currency_amount=getattr(node.final_fields, side))
        if (hasattr(node.final_fields, side))
        else None
    )
    previous_amount = (
        _parse_currency_amount(currency_amount=getattr(node.previous_fields, side))
        if (hasattr(node.previous_fields, side))
        else None
    )
    value = _calculate_delta(
        final_amount=final_amount,
        previous_amount=previous_amount,
    )

    change_amount = ChangeAmount(
        final_amount=final_amount.__dict__, previous_value=str(0 - value)
    )

    return change_amount


def _get_quality(node: NormalizedNode) -> str:
    """Calculate the offers quality.

    Args:
        node (NormalizedNode): Normalized node.

    Returns:
        str: The offers quality.
    """
    if node.final_fields is not None:
        taker_gets = cast(Union[AccountBalance, str], node.final_fields.TakerGets)
        taker_pays = cast(Union[AccountBalance, str], node.final_fields.TakerPays)
    elif node.new_fields is not None:
        taker_gets = cast(Union[AccountBalance, str], node.new_fields.TakerGets)
        taker_pays = cast(Union[AccountBalance, str], node.new_fields.TakerPays)
    else:
        taker_gets = "0"
        taker_pays = "0"

    taker_gets_value = (
        drops_to_xrp(taker_gets)
        if (isinstance(taker_gets, str))
        else Decimal(taker_gets.value)
    )
    taker_pays_value = (
        drops_to_xrp(taker_pays)
        if (isinstance(taker_pays, str))
        else Decimal(taker_pays.value)
    )

    if taker_gets_value > 0 and taker_pays_value > 0:
        return str(taker_pays_value / taker_gets_value)

    return "0"


def _ripple_to_unix_timestamp(rpepoch: int) -> int:
    return rpepoch + 0x386D4380


def _get_expiration_time(node: NormalizedNode) -> Optional[str]:
    """Formats the ripple timestamp to a easy to read format.

    Args:
        node (NormalizedNode): Normalized node.

    Returns:
        Optional[str]:
            Expiration time in a easy to read format.
    """
    if node.final_fields is not None:
        expiration_time = node.final_fields.Expiration
    elif node.new_fields is not None:
        expiration_time = node.new_fields.Expiration
    else:
        expiration_time = None

    if not isinstance(expiration_time, int):
        return expiration_time

    return str(
        datetime.utcfromtimestamp(_ripple_to_unix_timestamp(expiration_time)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )


def _remove_undefined(order: OrderChange) -> OrderChange:
    """Remove all attributes that are 'None'.

    Args:
        order (OrderChange):
            Order change.

    Returns:
        OrderChange:
            Cleaned up OrderChange object.
    """
    order_dict = order.__dict__.copy()

    for attr, value in order_dict.items():
        if value is None:
            delattr(order, attr)

    return order


def _calculate_received_and_paid_amount(
    taker_gets: CURRENCY_AMOUNT_TYPE,
    taker_pays: CURRENCY_AMOUNT_TYPE,
    direction: Literal["sell", "buy"],
) -> Tuple[CURRENCY_AMOUNT_TYPE, CURRENCY_AMOUNT_TYPE]:
    """Calculate what the taker had to pay and what he received.

    Args:
        taker_gets (CURRENCY_AMOUNT_TYPE):
            TakerGets amount.
        taker_pays (CURRENCY_AMOUNT_TYPE):
            TakerPays amount.
        direction (Literal["buy", "sell"]):
            'buy' or 'sell' offer.

    Returns:
        Tuple[CURRENCY_AMOUNT_TYPE, CURRENCY_AMOUNT_TYPE]:
            Both paid and received amount.
    """
    quantity = taker_pays if direction == "buy" else taker_gets
    total_price = taker_gets if direction == "buy" else taker_pays

    return quantity, total_price


def _convert_order_change(order: OrderChange) -> OrderChange:
    """Convert order change.

    Args:
        order (OrderChange):
            Order change.

    Returns:
        OrderChange:
            Converted order change.
    """
    taker_gets = order.taker_gets
    taker_pays = order.taker_pays
    direction: Literal["sell", "buy"] = "sell" if order.sell else "buy"
    quantity, total_price = _calculate_received_and_paid_amount(
        taker_gets=taker_gets,
        taker_pays=taker_pays,
        direction=direction,
    )

    order.direction = direction
    order.total_received = quantity
    order.total_paid = total_price

    return _remove_undefined(order=order)


def _parse_order_change(
    node: NormalizedNode,
) -> Dict[str, Union[Dict[str, str], bool, int, str]]:
    """Parse a change in the order book.

    Args:
        node (NormalizedNode):
            The affected node.

    Returns:
        Dict[str, Union[Dict[str, str], bool, int, str ]]:
            A order book change.
    """
    if node.final_fields is not None:
        seq = cast(int, node.final_fields.Sequence)
    elif node.new_fields is not None:
        seq = cast(int, node.new_fields.Sequence)

    if node.final_fields is not None:
        flags = cast(int, node.final_fields.Flags)
        sell = flags & LFS_SELL != 0
    else:
        sell = False

    order_change = OrderChange(
        taker_pays=_parse_change_amount(node, "TakerPays").__dict__,
        taker_gets=_parse_change_amount(node, "TakerGets").__dict__,
        sell=sell,
        sequence=seq,
        status=_parse_order_status(node),
        quality=_get_quality(node),
        expiration=_get_expiration_time(node),
    )
    order_change = _convert_order_change(order_change)

    if node.final_fields is not None:
        order_change.account = node.final_fields.Account
    elif node.new_fields is not None:
        order_change.account = node.new_fields.Account
    else:
        order_change.account = ""

    return order_change.__dict__


def compute_order_book_changes(
    nodes: List[NormalizedNode],
) -> List[Dict[str, Union[Dict[str, str], bool, int, str]]]:
    """Filter nodes by 'EntryType': 'Offer'.

    Args:
        nodes (List[NormalizedNode]): Affected nodes.

    Returns:
        List[Dict[str, Union[Dict[str, str], bool, int, str]]]:
            A unsorted list of all order book changes.
    """
    filter_nodes = map_(
        filter_(nodes, lambda node: True if node.entry_type == "Offer" else False),
        _parse_order_change,
    )

    return filter_nodes  # type: ignore
