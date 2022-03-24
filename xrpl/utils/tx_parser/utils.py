"""Utils for balance_changes and orderbook_changes."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Iterable, List, Optional, Union

from pydash import (  # type: ignore
    compact,
    filter_,
    flatten,
    group_by,
    is_empty,
    map_,
    map_values,
)
from typing_extensions import Literal

from xrpl.constants import XRPLException
from xrpl.utils.xrp_conversions import drops_to_xrp

"""
###########################################
Utils balance_parser and orderbook_parser
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
    """A standard format for nodes."""

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


def field_factory(
    field_state: Union[
        Literal["NewFields"], Literal["FinalFields"], Literal["PreviousFields"]
    ],
    fields: Any,
) -> Union[NewFields, FinalFields, PreviousFields]:
    """Set the attributes for 'NewFields', 'FinalFields' and 'ModifiedFields'.

    Args:
        field_state:
            State of the field.
        fields:
            A dictionary of all fields that field state has.
            E.g.: {'Balance': '62537659', 'OwnerCount': 16, 'Sequence': 67702065}

    Returns:
        The full field state with all its fields as objects.
    """

    def factory(name: str) -> Any:
        """Create a new class with variable name.

        Args:
            name (str): field name

        Returns:
            Any: A class with the name of a field. E.g. 'OwnerCount', 'Balance', ….
        """

        class NewClass:
            pass

        NewClass.__name__ = name

        return NewClass

    field_state_map: Dict[str, Union[NewFields, FinalFields, PreviousFields]] = {
        "NewFields": NewFields(),
        "FinalFields": FinalFields(),
        "PreviousFields": PreviousFields(),
    }

    field = field_state_map[field_state]

    for field_name, field_value in fields.items():
        # if 'field_value' is a dictionary
        if isinstance(field_value, dict):
            # if 'field_value' is a issued currency amount
            if field_name in ["Balance", "LowLimit", "HighLimit"]:
                field_value = Balance(
                    counterparty=field_value["issuer"],
                    currency=field_value["currency"],
                    value=field_value["value"],
                )
            else:  # if 'field_value' type is dict but is no issued currency amount.
                field_name_object = factory(field_name)
                for field_value_key, field_value_value in field_value.items():
                    setattr(field_name_object, field_value_key, field_value_value)
                field_value = field_name_object
        # set attributes to field state
        setattr(field, field_name, field_value)

    return field


def normalize_node(affectedNode: Dict[str, Any]) -> NormalizedNode:
    """Affected node to a standard format.

    Args:
        affectedNode (Dict[str, Any]):
            Affected node.

    Returns:
        NormalizedNode:
            NormalizedNode object.
    """
    diff_type = list(affectedNode)[0]
    node = affectedNode[diff_type]

    normalized_node = NormalizedNode(
        diffType=diff_type,
        entryType=node["LedgerEntryType"],
        ledgerIndex=node["LedgerIndex"],
        newFields=field_factory("NewFields", node["NewFields"])
        if ("NewFields" in node)
        else None,
        finalFields=field_factory("FinalFields", node["FinalFields"])
        if ("FinalFields" in node)
        else None,
        previousFields=field_factory("PreviousFields", node["PreviousFields"])
        if ("PreviousFields" in node)
        else None,
    )

    return normalized_node


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

    return map(normalize_node, affected_nodes)


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


class TrustLineQuantity(object):
    """Trust line quantity."""

    def __init__(self: object, address: str, balance: Dict[str, str]) -> None:
        """
        Args:
            address (str): Accounts address.
            balance (Dict[str, str]): Accounts balance.
        """
        self.address = address
        self.balance = Balance(
            counterparty=balance["counterparty"],
            currency=balance["currency"],
            value=balance["value"],
        )


def _parse_value(value: Any) -> Decimal:
    """Formats a balances value into a Decimal.

    Args:
        value (Any):
            Balance.

    Returns:
        Decimal: Balance as Decimal.
    """
    if hasattr(value, "value"):  # issued currency amount
        return Decimal(value.value)
    else:  # XRP amount
        return Decimal(value)


def parse_final_balance(node: NormalizedNode) -> Union[Decimal, None]:
    """Parse final balance.

    Args:
        node (NormalizedNode):
            Normalized node.

    Returns:
        Union[Decimal, None]:
            The balance value as Decimal.
    """
    if hasattr(node.new_fields, "Balance"):
        return _parse_value(node.new_fields.Balance)
    if hasattr(node.final_fields, "Balance"):
        return _parse_value(node.final_fields.Balance)

    return None


def compute_balance_changes(node: NormalizedNode) -> Union[None, int, Decimal]:
    """Compute balance changes.

    Args:
        node (NormalizedNode):
            Normalized node.

    Returns:
        Union[None, int, Decimal]:
            The parsed value.
    """
    value = None
    if hasattr(node.new_fields, "Balance"):
        value = _parse_value(node.new_fields.Balance)
    if hasattr(node.previous_fields, "Balance") and hasattr(
        node.final_fields, "Balance"
    ):
        value = _parse_value(node.final_fields.Balance) - _parse_value(
            node.previous_fields.Balance
        )

    if value and value != 0:
        return value
    else:
        return None


def _parse_xrp_quantity(
    node: NormalizedNode,
    valueParser: Any,
) -> Union[TrustLineQuantity, None]:
    """Parse XRP quantity.

    Args:
        node (NormalizedNode): Normalized node.
        valueParser (Any):
            Parser to get values needed.

    Returns:
        Union[TrustLineQuantity, None]:
            Trust line quantity.
    """
    value = valueParser(node)
    if value is None:
        return None

    # determine if the XRP value is negative
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
            "value": f"{drops_to_xrp(str(abs(int(value))))}"
            if not is_negative  # if XRP amount is positive
            else f"-{drops_to_xrp(str(abs(int(value))))}",  # if XRP is negative
        },
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
    """Parse trust line quantity.

    Args:
        node (NormalizedNode): Normalized node.
        valueParser (Any):
            Parser to get values needed.

    Returns:
        Union[None, List[TrustLineQuantity]]:
            Trust line quantity.
    """
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


def _group_by_address(
    balanceChanges: List[TrustLineQuantity],
) -> Any:
    """Groups the balances changes by address.

    Args:
        balanceChanges (List[TrustLineQuantity]):
            A list of trust line quantities.

    Returns:
        Any: A dictionary with all balance changes grouped by addresses.
    """
    grouped = group_by(balanceChanges, lambda node: node.address)

    return map_values(grouped, lambda group: map_(group, lambda node: node.balance))


def parse_quantities(
    metadata: Dict[str, Union[str, int, bool, Dict[str, Any]]],
    valueParser: Any,
) -> Any:
    """Parse final balance.

    Args:
        metadata (Dict[str, Union[str, int, bool, Dict[str, Any]]):
            The transactions metadata.
        valueParser (Any):
            Value parser.

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


class OrderChange:
    """Order change."""

    def __init__(
        self: Any,
        taker_pays: Union[Dict[str, str], str],
        taker_gets: Union[Dict[str, str], str],
        sell: bool,
        sequence: int,
        status: Optional[
            Union[
                Literal["created"],
                Literal["partially-filled"],
                Literal["filled"],
                Literal["cancelled"],
            ]
        ],
        quality: str,
        expiration: Optional[Union[Any, str]],
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


def group_by_address_order_book(
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


def _parse_currency_amount(currency_amount: Union[str, Any]) -> Balance:
    """Parses an accounts balance and formats it into a standard format.

    Args:
        currency_amount (Union[str, Any]):
            Currency amount.

    Returns:
        Balance: Currency balance.
    """
    if isinstance(currency_amount, str):
        return Balance(
            currency="XRP", counterparty="", value=str(drops_to_xrp(currency_amount))
        )

    return Balance(
        currency=currency_amount.currency,
        counterparty=currency_amount.issuer,
        value=currency_amount.value,
    )


def _calculate_delta(
    final_amount: Union[Balance, None],
    previous_amount: Union[Balance, None],
) -> Union[Decimal, int]:
    if isinstance(final_amount, Balance) and isinstance(previous_amount, Balance):
        previous_value = Decimal(previous_amount.value)
        return 0 - previous_value

    return 0


def _parse_order_status(
    node: NormalizedNode,
) -> Union[
    Literal["created"],
    Literal["partially-filled"],
    Literal["filled"],
    Literal["cancelled"],
    None,
]:
    """Parses the status of an order.

    Returns:
        The order status
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
) -> Any:
    """Parse the changed amount of an order.

    Args:
        node (NormalizedNode): Normalized node.
        side (Literal[&quot;TakerPays&quot;, &quot;TakerGets&quot;]):
            Side of the order to parse.

    Returns:
        Any:
            The changed currency amount.
    """
    status = _parse_order_status(node)

    if status == "cancelled":
        return (
            _parse_currency_amount(getattr(node.final_fields, side))
            if (hasattr(node.final_fields, side))
            else None
        )
    if status == "created":
        return (
            _parse_currency_amount(getattr(node.new_fields, side))
            if (hasattr(node.new_fields, side))
            else None
        )

    # Else it has modified an offer.
    # Status is 'partially-filled' or 'filled'.
    final_amount = (
        _parse_currency_amount(getattr(node.final_fields, side))
        if (hasattr(node.final_fields, side))
        else None
    )
    previous_amount = (
        _parse_currency_amount(getattr(node.previous_fields, side))
        if (hasattr(node.previous_fields, side))
        else None
    )
    value = _calculate_delta(final_amount, previous_amount)

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
    taker_gets_value = (
        drops_to_xrp(taker_gets) if (isinstance(taker_gets, str)) else taker_gets.value
    )
    taker_pays_value = (
        drops_to_xrp(taker_pays) if (isinstance(taker_pays, str)) else taker_pays.value
    )

    if Decimal(taker_gets_value) > 0 and Decimal(taker_pays_value) > 0:
        return str(Decimal(taker_pays_value) / Decimal(taker_gets_value))

    return "0"


def _ripple_to_unix_timestamp(rpepoch: int) -> int:
    return rpepoch + 0x386D4380


def _get_expiration_time(node: NormalizedNode) -> Union[Any, None]:
    """Formats the ripple timestamp to a easy to read format.

    Args:
        node (NormalizedNode): Normalized node.

    Returns:
        Union[Any, None]:
            Expiration time in a easy to read format.
    """
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
    """Remove all attributes that are 'None'.

    Args:
        order (OrderChange): Order change.

    Returns:
        OrderChange:
            Cleaned up OrderChange object.
    """
    order_dict = order.__dict__.copy()

    for k, v in order_dict.items():
        if v is None:
            delattr(order, k)

    return order


def _calculate_received_and_paid_amount(
    taker_gets: Any,
    taker_pays: Any,
    direction: str,
) -> Any:
    """Calculate what the taker had to pay and what he received.

    Args:
        taker_gets (Any): TakerGets amount.
        taker_pays (Any): TakerPays amount.
        direction (str): 'buy' or 'sell' offer.

    Returns:
        Any:
            Both paid and received amount.
    """
    quantity = taker_pays if direction == "buy" else taker_gets
    total_price = taker_gets if direction == "buy" else taker_pays

    return quantity, total_price


def _convert_order_change(order: OrderChange) -> OrderChange:
    """Convert order change.

    Args:
        order (OrderChange): Order change.

    Returns:
        OrderChange: Converted order change.
    """
    taker_gets = order.taker_gets
    taker_pays = order.taker_pays
    direction = "sell" if order.sell else "buy"
    quantity, total_price = _calculate_received_and_paid_amount(
        taker_gets, taker_pays, direction
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
        node (NormalizedNode): The affected node.

    Returns:
        Dict[str, Union[ Dict[str, str], bool, int, str ]]: A order book change.
    """
    order_change = OrderChange(
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
    order_change = _convert_order_change(order_change)

    order_change.account = (
        node.final_fields.Account
        if (hasattr(node.final_fields, "Account"))
        else node.new_fields.Account
    )

    return order_change.__dict__


def parse_order_book_changes(
    nodes: Iterable[NormalizedNode],
) -> Any:
    """Filter nodes by 'EntryType': 'Offer'.

    Args:
        nodes (Iterable[NormalizedNode]): Affected nodes.

    Returns:
        Any:
            A list of all nodes with 'EntryType': 'Offer'
    """
    filter_nodes = map_(
        filter_(nodes, lambda node: True if node.entry_type == "Offer" else False),
        _parse_order_change,
    )

    return filter_nodes
