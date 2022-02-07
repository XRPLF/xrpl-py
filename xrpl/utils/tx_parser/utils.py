"""Utils for balance_changes and orderbook_changes."""

from datetime import datetime
from typing import Any, Dict, Iterable, List, Literal, Union

from pydash import (  # type: ignore
    compact,
    filter_,
    flatten,
    group_by,
    is_empty,
    map_,
    map_values,
)

from xrpl.constants import XRPLException
from xrpl.utils.xrp_conversions import drops_to_xrp

"""
###########################################
Utils balance_changes and orderbook_changes
###########################################
"""


class XRPLMetadataException(XRPLException):
    """Exception for invalid transaction metadata."""

    pass


def is_valid_metadata(metadata: Dict[str, Any]) -> None:
    """Check if the given metadata is valid.

    Args:
        metadata (Dict[str, Any]): The transactions metadata

    Raises:
        XRPLMetadataException: If field Account is missing.
        XRPLMetadataException: If field Account is missing.
        XRPLMetadataException: If field meta is missing.
        XRPLMetadataException: If field AffectedNodes is missing or is empty.
    """
    if "transaction" in metadata:
        if "Account" not in metadata["transaction"]:
            raise XRPLMetadataException(
                "Metadata incomplete: Metadata field 'Account' must be included."
            )
    elif "Account" not in metadata:
        raise XRPLMetadataException(
            "Metadata incomplete: Metadata field 'Account' must be included."
        )

    if "meta" not in metadata:
        raise XRPLMetadataException(
            "Metadata incomplete: Metadata field 'meta' must be included."
        )

    if "AffectedNodes" not in metadata["meta"] or not metadata["meta"]["AffectedNodes"]:
        raise XRPLMetadataException("Metadata incomplete: No nodes provided.")


class NormalizedNode:
    """Normalized Node"""

    def __init__(
        self: Any,
        diffType: str,
        entryType: str,
        ledgerIndex: str,
        newFields: Any,
        finalFields: Any,
        previousFields: Any,
    ) -> None:
        """
        Args:
            diffType (str): Node type (ModifiedNode, CreatedNode or DeletedNode).
            entryType (str): Entry type (e.g. Offer, AccountRoot, …).
            ledgerIndex (str): Ledger index.
            newFields (Any): New fields.
            finalFields (Any):
            Fields after the transaction occurred.
            previousFields (Any):
            Fields before the transaction occurred.
        """
        self.diff_type = diffType
        self.entry_type = entryType
        self.ledger_index = ledgerIndex
        self.new_fields = newFields
        self.final_fields = finalFields
        self.previous_fields = previousFields


class NewFields:
    """NewFields"""

    pass


class FinalFields:
    """FinalFields"""

    pass


class PreviousFields:
    """PreviousFields"""

    pass


def _field_factory(
    field_name: Union[
        Literal["NewFields"], Literal["FinalFields"], Literal["PreviousFields"]
    ],
    fields: Dict[str, Any],
) -> Union[NewFields, FinalFields, PreviousFields]:
    def factory(name: str) -> Any:
        class NewClass:
            pass

        NewClass.__name__ = name

        return NewClass

    field_names: Dict[str, Union[NewFields, FinalFields, PreviousFields]] = {
        "NewFields": NewFields(),
        "FinalFields": FinalFields(),
        "PreviousFields": PreviousFields(),
    }

    field = field_names[field_name]

    for k, v in fields.items():
        if isinstance(v, dict):
            if k in ["Balance", "LowLimit", "HighLimit"]:
                v = Balance(
                    counterparty=v["issuer"], currency=v["currency"], value=v["value"]
                )
            else:
                fac = factory(k)
                for vk, vv in v.items():
                    setattr(fac, vk, vv)
                v = fac
        setattr(field, k, v)

    return field


def _normalize_node(affectedNode: Dict[str, Any]) -> NormalizedNode:
    diff_type = list(affectedNode)[0]
    node = affectedNode[diff_type]

    n = NormalizedNode(
        diffType=diff_type,
        entryType=node["LedgerEntryType"],
        ledgerIndex=node["LedgerIndex"],
        newFields=_field_factory("NewFields", node["NewFields"])
        if ("NewFields" in node)
        else None,
        finalFields=_field_factory("FinalFields", node["FinalFields"])
        if ("FinalFields" in node)
        else None,
        previousFields=_field_factory("PreviousFields", node["PreviousFields"])
        if ("PreviousFields" in node)
        else None,
    )

    return n


def normalize_nodes(metadata: Dict[str, Any]) -> Iterable[NormalizedNode]:
    """Normalize nodes.

    Args:
        metadata (Dict[str, Any]): Transctions metadata

    Returns:
        Iterable[NormalizedNode]: The normalized nodes
    """
    affected_nodes = metadata["meta"]["AffectedNodes"]
    if not affected_nodes:
        return []

    return map(_normalize_node, affected_nodes)


"""
#####################
Utils balance_changes
#####################
"""


class Balance:
    """A accounts balance."""

    def __init__(self: Any, counterparty: str, currency: str, value: str) -> None:
        """
        Args:
            counterparty (str): Counterparty
            currency (str): Currency
            value (str): Value
        """
        self.counterparty = counterparty
        self.currency = currency
        self.value = value


class TrustLineQuantity:
    """Trust line quantity."""

    def __init__(self: Any, address: str, balance: Dict[str, str]) -> None:
        """
        Args:
            address (str): Address
            balance (Dict[str, str]): Balance
        """
        self.address = address
        self.balance = Balance(
            counterparty=balance["counterparty"],
            currency=balance["currency"],
            value=balance["value"],
        )


def _parse_value(value: Any) -> float:
    if hasattr(value, "value"):
        return float(value.value)
    else:
        return float(value)


def parse_final_balance(node: NormalizedNode) -> Union[float, None]:
    """Parse final balance.

    Args:
        node (NormalizedNode): [description]

    Returns:
        Union[float, None]: [description]
    """
    if hasattr(node.new_fields, "Balance"):
        return _parse_value(node.new_fields.Balance)
    elif hasattr(node.final_fields, "Balance"):
        return _parse_value(node.final_fields.Balance)

    return None


def compute_balance_changes(node: NormalizedNode) -> Union[None, int, float]:
    """Compute balance changes.

    Args:
        node (NormalizedNode): Node

    Returns:
        Union[None, int, float]: The parsed value
    """
    value = None
    if hasattr(node.new_fields, "Balance"):
        value = _parse_value(node.new_fields.Balance)
    elif hasattr(node.previous_fields, "Balance") and hasattr(
        node.final_fields, "Balance"
    ):
        value = _parse_value(node.final_fields.Balance) - _parse_value(
            node.previous_fields.Balance
        )

    return None if value is None else None if value == 0 else value


def _parse_xrp_quantity(
    node: NormalizedNode,
    valueParser: Any,
) -> Union[TrustLineQuantity, None]:
    value = valueParser(node)
    if value is None:
        return None
    is_negative = False
    if str(value).startswith("-"):
        is_negative = True
    result = TrustLineQuantity(
        address=node.final_fields.Account
        if node.final_fields
        else node.new_fields.Account,
        balance={
            "counterparty": "",
            "currency": "XRP",
            "value": str(drops_to_xrp(str(abs(int(value)))))
            if not is_negative
            else "-{}".format(drops_to_xrp(str(abs(int(value))))),
        },
    )

    return result


def _flip_trustline_perspective(quantity: TrustLineQuantity) -> TrustLineQuantity:
    negated_balance = abs(float(quantity.balance.value))
    result = TrustLineQuantity(
        address=quantity.balance.counterparty,
        balance={
            "counterparty": quantity.address,
            "currency": quantity.balance.currency,
            "value": str(negated_balance),
        },
    )

    return result


def _parse_trustline_quantity(
    node: NormalizedNode,
    valueParser: Any,
) -> Union[None, List[TrustLineQuantity]]:
    value = valueParser(node)
    if value is None:
        return None
    fields = node.final_fields if is_empty(node.new_fields) else node.new_fields
    result = TrustLineQuantity(
        address=fields.LowLimit.counterparty,
        balance={
            "counterparty": fields.HighLimit.counterparty,
            "currency": fields.Balance.currency,
            "value": str(value),
        },
    )

    return [result, _flip_trustline_perspective(result)]


def _group_by_address(balanceChanges: Any) -> Any:
    grouped = group_by(balanceChanges, lambda node: node.address)

    return map_values(grouped, lambda group: map_(group, lambda node: node.balance))


def parse_quantities(
    metadata: Dict[str, Union[str, int, bool, Dict[str, Any]]], valueParser: Any
) -> Any:
    """Parse final balance.

    Args:
        metadata (Dict[str, Union[str, int, bool, Dict[str, Any]]):
            The transactions metadata
        valueParser (Any):
            Value parser

    Returns:
        Any: The grouped balance changes.
    """
    values: List[Any] = []
    for node in normalize_nodes(metadata=metadata):
        if node.entry_type == "AccountRoot":
            values.append(_parse_xrp_quantity(node, valueParser))
        elif node.entry_type == "RippleState":
            values.append(_parse_trustline_quantity(node, valueParser))
        else:
            values.append([])

    return _group_by_address(compact(flatten(values)))


"""
########################
Utils orderbook_changes
########################
"""

lfs_sell = 0x00020000


class XRPLNoOffersAffectedException(XRPLException):
    """Exception if the transaction did not affected any offers"""

    pass


class OrderChange:
    """Order change"""

    def __init__(
        self: Any,
        taker_pays: Union[Dict[str, str], str],
        taker_gets: Union[Dict[str, str], str],
        sell: bool,
        sequence: int,
        status: Union[
            Literal["created"],
            Literal["partially-filled"],
            Literal["filled"],
            Literal["cancelled"],
            None,
        ],
        quality: str,
        expiration: Union[Any, str, None],
        direction: str = "",
        total_received: Union[Dict[str, str], str] = {},
        total_paid: Union[Dict[str, str], str] = {},
        account: str = "",
    ) -> None:
        """
        Args:
            taker_pays (Union[Dict[str, str], str]): TakerPays
            taker_gets (Union[Dict[str, str], str]): TakerGets
            sell (bool): If flag 'sell' is set
            sequence (int): Sequence
            status (str): Status
            quality (str): Quality
            expiration (Union[Any, str, None]): Expiration
            direction (str, optional): Buy or Sell. Defaults to None.
            total_received (Union[Dict[str, str], str], optional):
            Amount received. Defaults to None.
            total_paid (Union[Dict[str, str], str], optional): Costs. Defaults to None.
            account (str, optional): Account. Defaults to None.
        """
        self.taker_pays = taker_pays
        self.taker_gets = taker_gets
        self.sell = sell
        self.sequence = sequence
        self.status = status
        self.quality = quality
        self.expiration = expiration
        self.direction = direction
        self.total_received = total_received
        self.total_paid = total_paid
        self.account = account


class CurrencyAmount:
    """Currency amount"""

    def __init__(self: Any, currency: str, counterparty: str, value: str) -> None:
        """
        Args:
            currency (str): Currency
            counterparty (str): Counterparty
            value (str): Value
        """
        self.currency = currency
        self.counterparty = counterparty
        self.value = value


class ChangeAmount:
    """Amount changed by transaction."""

    def __init__(self: Any, final_amount: Dict[str, str], previous_value: str) -> None:
        """
        Args:
            final_amount (Dict[str, str]): Final amount
            previous_value (str): Difference to Previous amount
        """
        self.final_amount = final_amount
        self.previous_value = previous_value


def group_by_address_order(
    order_changes: List[Dict[str, Union[Dict[str, str], bool, int, str]]]
) -> Any:
    """Group order book changes by addresses.

    Args:
        order_changes (List[Dict[str, Union[Dict[str, str], bool, int, str]]]):
            Order book changes

    Returns:
        Dict[str, List[Dict[str, Any]]]:
            Order book changes grouped by addresses.
    """
    return group_by(order_changes, lambda change: change["account"])


def _parse_currency_amount(currency_amount: Union[str, Any]) -> CurrencyAmount:
    if isinstance(currency_amount, str):
        return CurrencyAmount(
            currency="XRP", counterparty="", value=str(drops_to_xrp(currency_amount))
        )

    return CurrencyAmount(
        currency=currency_amount.currency,
        counterparty=currency_amount.issuer,
        value=currency_amount.value,
    )


def _calculate_delta(
    final_amount: Union[CurrencyAmount, None],
    previous_amount: Union[CurrencyAmount, None],
) -> str:
    if isinstance(final_amount, CurrencyAmount) and isinstance(
        previous_amount, CurrencyAmount
    ):
        final_value = float(final_amount.value)
        previous_value = float(previous_amount.value)
        return str(final_value - previous_value)

    return "0"


def _parse_order_status(
    node: NormalizedNode,
) -> Union[
    Literal["created"],
    Literal["partially-filled"],
    Literal["filled"],
    Literal["cancelled"],
    None,
]:
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
    node: NormalizedNode, type: Literal["TakerPays", "TakerGets"]
) -> Union[CurrencyAmount, ChangeAmount, None]:
    status = _parse_order_status(node)

    if status == "cancelled":
        return (
            _parse_currency_amount(getattr(node.final_fields, type))
            if (hasattr(node.final_fields, type))
            else None
        )
    elif status == "created":
        return (
            _parse_currency_amount(getattr(node.new_fields, type))
            if (hasattr(node.new_fields, type))
            else None
        )

    final_amount = (
        _parse_currency_amount(getattr(node.final_fields, type))
        if (hasattr(node.final_fields, type))
        else None
    )
    previous_amount = (
        _parse_currency_amount(getattr(node.previous_fields, type))
        if (hasattr(node.previous_fields, type))
        else None
    )
    value = _calculate_delta(final_amount, previous_amount)

    d = ChangeAmount(
        final_amount=final_amount.__dict__, previous_value=str(0 - float(value))
    )

    return d


def _adjust_quality_for_xrp(
    quality: str, taker_gets_currency: str, taker_pays_currency: str
) -> str:
    numerator_shift = -6 if taker_pays_currency == "XRP" else 0
    denominator_shift = -6 if taker_gets_currency == "XRP" else 0
    shift = numerator_shift - denominator_shift

    if shift == 0:
        return f"{quality}"
    else:
        quality = str(float(quality) * 1000000.0)
        return quality


def _parse_quality(
    quality_hex: str, taker_gets_currency: str, taker_pays_currency: str
) -> str:
    assert len(quality_hex) == 16
    mantissa = int(quality_hex[2:], 16)
    offset = int(quality_hex[:2], 16) - 100
    quality = f"{mantissa}e{offset}"

    return _adjust_quality_for_xrp(
        quality=quality,
        taker_gets_currency=taker_gets_currency,
        taker_pays_currency=taker_pays_currency,
    )


def _get_quality(node: NormalizedNode) -> str:
    taker_gets = (
        node.final_fields.TakerGets
        if (hasattr(node.final_fields, "TakerGets"))
        else node.new_fields.TakerGets
    )
    taker_pays = (
        node.final_fields.TakerPays
        if (hasattr(node.final_fields, "TakerPays"))
        else node.new_fields.TakerPays
    )
    taker_gets_currency = (
        "XRP" if (isinstance(taker_gets, str)) else taker_gets.currency
    )
    taker_pays_currency = (
        "XRP" if (isinstance(taker_pays, str)) else taker_pays.currency
    )
    book_directory = (
        node.final_fields.BookDirectory
        if (hasattr(node.final_fields, "BookDirectory"))
        else node.new_fields.BookDirectory
    )
    quality_hex = book_directory[-16:]

    return _parse_quality(
        quality_hex=quality_hex,
        taker_gets_currency=taker_gets_currency,
        taker_pays_currency=taker_pays_currency,
    )


def _ripple_to_unix_timestamp(rpepoch: int) -> int:
    return rpepoch + 0x386D4380


def _get_expiration_time(node: NormalizedNode) -> Union[Any, str, None]:
    expiration_time = (
        node.final_fields.Expiration
        if (hasattr(node.final_fields, "Expiration"))
        else node.new_fields.Expiration
        if (hasattr(node.new_fields, "Expiration"))
        else None
    )
    if not isinstance(expiration_time, int):
        return expiration_time

    return str(
        datetime.utcfromtimestamp(_ripple_to_unix_timestamp(expiration_time)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )


def _remove_undefined(order: OrderChange) -> OrderChange:
    order_dict = order.__dict__.copy()

    for k, v in order_dict.items():
        if v is None:
            delattr(order, k)

    return order


def _convert_order_change(order: OrderChange) -> OrderChange:
    taker_gets = order.taker_gets
    taker_pays = order.taker_pays
    direction = "sell" if order.sell else "buy"
    quantity = taker_pays if direction == "buy" else taker_gets
    total_price = taker_gets if direction == "buy" else taker_pays

    order.direction = direction
    order.total_received = quantity
    order.total_paid = total_price

    return _remove_undefined(order=order)


def _parse_order_change(
    node: NormalizedNode,
) -> Dict[str, Union[Dict[str, str], bool, int, str]]:
    """Parse a change in the order book.

    Args:
        node (NormalizedNode): The affected node.

    Returns:
        Dict[str, Union[ Dict[str, str], bool, int, str ]]: A order book change.
    """
    order_change = _convert_order_change(
        OrderChange(
            taker_pays=_parse_change_amount(node, "TakerPays").__dict__,
            taker_gets=_parse_change_amount(node, "TakerGets").__dict__,
            sell=node.final_fields.Flags & lfs_sell != 0
            if (node.final_fields is not None)
            else False,
            sequence=node.final_fields.Sequence
            if hasattr(node.final_fields, "Sequence")
            else node.new_fields.Sequence,
            status=_parse_order_status(node),
            quality=_get_quality(node),
            expiration=_get_expiration_time(node),
        )
    )

    order_change.account = (
        node.final_fields.Account
        if (hasattr(node.final_fields, "Account"))
        else node.new_fields.Account
    )

    return order_change.__dict__


def filter_nodes(
    nodes: Iterable[NormalizedNode],
) -> Any:
    """Filter nodes by 'EntryType': 'Offer'.

    Args:
        nodes (Iterable[NormalizedNode]): Affected nodes.

    Returns:
        List[Dict[str, Union[Dict[str, str], bool, int, str]]]:
            A list of all nodes with 'EntryType': 'Offer'
    """
    filter_nodes = map_(
        filter_(nodes, lambda node: True if node.entry_type == "Offer" else False),
        _parse_order_change,
    )

    return filter_nodes
