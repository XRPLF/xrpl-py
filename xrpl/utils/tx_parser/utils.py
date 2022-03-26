"""Utils for balance_changes and orderbook_changes."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union

from pydash import compact, filter_, flatten, group_by, map_, map_values  # type: ignore
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
        metadata (Dict[str, Any]):
            The transactions metadata

    Raises:
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


def normalize_metadata(
    metadata: Dict[
        str,
        Union[
            str,
            int,
            Dict[str, str],
            List[List[Dict[str, Union[str, int]]]],
            Dict[
                str,
                List[
                    Dict[
                        str,
                        Dict[
                            str,
                            Union[str, int, Dict[str, Union[str, int, Dict[str, str]]]],
                        ],
                    ],
                ],
            ],
        ],
    ],
) -> Dict[  # metadata received from a tx method
    str,
    Union[
        str,
        int,
        Dict[str, str],  # issued currency amount
        List[List[Dict[str, Union[str, int]]]],  # Field: 'paths'
        Dict[  # Field: 'meta'
            str,  # Field: 'AffectedNodes'
            List[
                Dict[
                    str,  # Node state
                    Dict[
                        str,
                        Union[str, int, Dict[str, Union[str, int, Dict[str, str]]]],
                    ],
                ],
            ],
        ],
    ],
]:
    """Formats the transaction metadata into one standard format.

    Args:
        metadata:
            Transactions metadata.

    Returns:
        Metadata in standard format.
    """
    transaction = metadata["transaction"]
    assert isinstance(transaction, dict)
    normalized_metadata = {
        tx_field_name: tx_field_value
        for tx_field_name, tx_field_value in transaction.items()
    }

    meta = metadata["meta"]
    assert isinstance(meta, dict)
    normalized_metadata["meta"] = meta  # type: ignore
    ledger_index = metadata["ledger_index"]
    assert isinstance(ledger_index, int)
    normalized_metadata["ledger_index"] = ledger_index  # type: ignore

    return normalized_metadata  # type: ignore


class FieldName:
    """FieldName"""

    currency: str
    issuer: str
    value: str


class FieldState:
    """FieldState"""

    Balance: Union[AccountBalance, str]
    LowLimit: Union[AccountBalance, str]
    HighLimit: Union[AccountBalance, str]
    Account: str
    TakerGets: Union[FieldName, str]  # Type: 'NewClass'
    TakerPays: Union[FieldName, str]  # Type: 'NewClass'
    Sequence: int
    Flags: int
    Expiration: Optional[Union[int, str]] = None


class NewFields(FieldState):
    """NewFields"""

    pass


class FinalFields(FieldState):
    """FinalFields"""

    pass


class PreviousFields(FieldState):
    """PreviousFields"""

    pass


class NormalizedNode:
    """A standard format for nodes."""

    def __init__(
        self: NormalizedNode,
        diff_type: str,
        entry_type: str,
        ledger_index: str,
        new_fields: Optional[FieldState],
        final_fields: Optional[FieldState],
        previous_fields: Optional[FieldState],
    ) -> None:
        """
        Args:
            diffType (str): Node type (ModifiedNode, CreatedNode or DeletedNode).
            entryType (str): Entry type (e.g. Offer, AccountRoot, …).
            ledgerIndex (str): Ledger index.
            newFields (Optional[FieldState]):
                New fields.
            finalFields (Optional[FieldState]):
                Fields after the transaction occurred.
            previousFields (Optional[FieldState]):
                Fields before the transaction occurred.
        """
        self.diff_type = diff_type
        self.entry_type = entry_type
        self.ledger_index = ledger_index
        self.new_fields = new_fields
        self.final_fields = final_fields
        self.previous_fields = previous_fields


def field_factory(
    field_state: FieldState,
    fields: Dict[str, Union[str, int, Dict[str, str]]],
) -> FieldState:
    """Set the attributes for 'NewFields', 'FinalFields' and 'ModifiedFields'.

    Args:
        field_state (FieldState):
            State of the field.
        fields (Dict[str, Union[str, int, Dict[str, str]]]):
            A dictionary of all fields that field state has.
            E.g.: {'Balance': '62537659', 'OwnerCount': 16, 'Sequence': 67702065}

    Returns:
        FieldState:
            The full field state with all its fields as objects.
    """

    def factory(name: str) -> Type[FieldName]:
        """Create a new class with variable name.

        Args:
            name (str):
                Field name.

        Returns:
            Type[FieldName]:
                A class with the name of a field. E.g. 'OwnerCount', 'Balance', ….
        """

        class NewClass(FieldName):
            pass

        NewClass.__name__ = name

        return NewClass

    for field_name, field_value in fields.items():
        # if 'field_value' is a dictionary
        if isinstance(field_value, dict):
            # if 'field_value' is a issued currency amount
            if field_name in ["Balance", "LowLimit", "HighLimit"]:
                new_field_value = AccountBalance(
                    counterparty=field_value["issuer"],
                    currency=field_value["currency"],
                    value=field_value["value"],
                )
                setattr(field_state, field_name, new_field_value)
            else:  # if 'field_value' type is dict but is no issued currency amount.
                field_name_object = factory(field_name)
                for field_value_key, field_value_value in field_value.items():
                    setattr(field_name_object, field_value_key, field_value_value)
                setattr(field_state, field_name, field_name_object)
        else:
            setattr(field_state, field_name, field_value)

    return field_state


def normalize_node(
    affected_node: Dict[
        str,  # Node state / diff_type
        Dict[
            str,
            Union[str, int, Dict[str, Union[str, int, Dict[str, str]]]],
        ],
    ]
) -> NormalizedNode:
    """Affected node to a standard format.

    Args:
        affected_node (Dict[str, Dict[str, Union[str, int,
        Dict[str, Union[str, int, Dict[str, str]]]]]]):
            Affected node.

    Returns:
        NormalizedNode:
            NormalizedNode object.
    """
    diff_type: str = list(affected_node.keys())[0]
    node_fields = list(affected_node.values())[0]

    ledger_entry_type = str(node_fields["LedgerEntryType"])
    ledger_index = str(node_fields["LedgerIndex"])

    new_fields = None
    if "NewFields" in node_fields:
        assert isinstance(node_fields["NewFields"], dict)
        new_fields = field_factory(NewFields(), node_fields["NewFields"])

    final_fields = None
    if "FinalFields" in node_fields:
        assert isinstance(node_fields["FinalFields"], dict)
        final_fields = field_factory(NewFields(), node_fields["FinalFields"])

    previous_fields = None
    if "PreviousFields" in node_fields:
        assert isinstance(node_fields["PreviousFields"], dict)
        previous_fields = field_factory(NewFields(), node_fields["PreviousFields"])

    normalized_node = NormalizedNode(
        diff_type=diff_type,
        entry_type=ledger_entry_type,
        ledger_index=ledger_index,
        new_fields=new_fields,
        final_fields=final_fields,
        previous_fields=previous_fields,
    )

    return normalized_node


def normalize_nodes(
    metadata: Dict[
        str,
        Union[
            str,
            int,
            Dict[str, str],
            List[List[Dict[str, Union[str, int]]]],
            Dict[
                str,
                List[
                    Dict[
                        str,
                        Dict[
                            str,
                            Union[str, int, Dict[str, Union[str, int, Dict[str, str]]]],
                        ],
                    ],
                ],
            ],
        ],
    ],
) -> List[NormalizedNode]:
    """Normalize nodes.

    Args:
        metadata:
            Transctions metadata

    Returns:
        List[NormalizedNode]: The normalized nodes
    """
    meta = metadata["meta"]
    if isinstance(meta, dict):
        affected_nodes = meta["AffectedNodes"]
        if not affected_nodes:
            return []
        assert isinstance(affected_nodes, list)
        return map_(affected_nodes, normalize_node)  # type: ignore
    else:
        return []


"""
#####################
Utils balance_changes
#####################
"""


class AccountBalance:
    """A accounts balance."""

    def __init__(
        self: AccountBalance, counterparty: str, currency: str, value: str
    ) -> None:
        """
        Args:
            counterparty (str):
                Counterparty
            currency (str):
                Currency
            value (str):
                Value
        """
        self.counterparty = counterparty
        self.currency = currency
        self.value = value


class TrustLineQuantity:
    """Trust line quantity."""

    def __init__(
        self: TrustLineQuantity,
        address: str,
        balance: Dict[str, str],
    ) -> None:
        """
        Args:
            address (str):
                Accounts address.
            balance (Dict[str, str]):
                Accounts balance.
        """
        self.address = address
        self.balance = AccountBalance(
            counterparty=balance["counterparty"],
            currency=balance["currency"],
            value=balance["value"],
        )


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


def parse_final_balance(node: NormalizedNode) -> Union[Decimal, None]:
    """Parse final balance.

    Args:
        node (NormalizedNode):
            Normalized node.

    Returns:
        Union[Decimal, None]:
            The balance value as Decimal.
    """
    if node.new_fields and hasattr(node.new_fields, "Balance"):
        return _parse_value(value=node.new_fields.Balance)
    if node.final_fields and hasattr(node.final_fields, "Balance"):
        return _parse_value(value=node.final_fields.Balance)

    return None


def compute_balance_changes(node: NormalizedNode) -> Union[Decimal, None]:
    """Compute balance changes.

    Args:
        node (NormalizedNode):
            Normalized node.

    Returns:
        Union[Decimal, None]:
            The parsed value.
    """
    value = None
    if isinstance(node.new_fields, NewFields) and hasattr(node.new_fields, "Balance"):
        value = _parse_value(value=node.new_fields.Balance)
    if (
        node.previous_fields is not None
        and hasattr(node.previous_fields, "Balance")
        and node.final_fields is not None
        and hasattr(node.final_fields, "Balance")
    ):
        value = _parse_value(value=node.final_fields.Balance) - _parse_value(
            value=node.previous_fields.Balance
        )

    if value and value != 0:
        return value
    else:
        return None


def _parse_xrp_quantity(
    node: NormalizedNode,
    value_parser: Callable[[NormalizedNode], Union[Decimal, None]],
) -> Union[TrustLineQuantity, None]:
    """Parse XRP quantity.

    Args:
        node (NormalizedNode):
            Normalized node.
        value_parser (Callable[[NormalizedNode], Union[Decimal, None]]):
            Parser to get values needed.

    Returns:
        Union[TrustLineQuantity, None]:
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
        address = node.final_fields.Account
    elif node.new_fields is not None:
        address = node.new_fields.Account
    else:
        address = ""

    result = TrustLineQuantity(
        address=address,
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
    value_parser: Callable[[NormalizedNode], Union[Decimal, None]],
) -> Union[List[TrustLineQuantity], None]:
    """Parse trust line quantity.

    Args:
        node (NormalizedNode):
            Normalized node.
        value_parser (Callable[[NormalizedNode], Union[Decimal, None]]):
            Parser to get values needed.

    Returns:
        Union[List[TrustLineQuantity], None]:
            Trust line quantity.
    """
    value = value_parser(node)
    if value is None:
        return None
    fields = node.final_fields if node.new_fields is None else node.new_fields

    if fields is None:
        return None

    assert isinstance(fields.LowLimit, AccountBalance)
    assert isinstance(fields.HighLimit, AccountBalance)
    assert isinstance(fields.Balance, AccountBalance)

    result = TrustLineQuantity(
        address=fields.LowLimit.counterparty,
        balance={
            "counterparty": fields.HighLimit.counterparty,
            "currency": fields.Balance.currency,
            "value": str(value),
        },
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
    value_parser: Callable[[NormalizedNode], Union[Decimal, None]],
) -> Dict[str, List[AccountBalance]]:
    """Parse final balance.

    Args:
        nodes (List[NormalizedNode]):
            Normalized nodes.
        value_parser (Callable[[NormalizedNode], Union[Decimal, None]]):
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


"""
########################
Utils orderbook_changes
########################
"""


lfs_sell = 0x00020000


class OrderChange:
    """Order change."""

    def __init__(
        self: OrderChange,
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
        expiration: Optional[Union[int, str]],
        direction: str = "",
        total_received: Union[Dict[str, str], str] = {},
        total_paid: Union[Dict[str, str], str] = {},
        account: str = "",
    ) -> None:
        """
        Args:
            taker_pays (Union[Dict[str, str], str]):
                TakerPays
            taker_gets (Union[Dict[str, str], str]):
                TakerGets
            sell (bool):
                If flag 'sell' is set
            sequence (int):
                Sequence
            status (Optional[Union[Literal["created"], Literal["partially-filled"],
            Literal["filled"], Literal["cancelled"]]]):
                Status
            quality (str):
                Quality
            expiration (Optional[Union[int, str]]):
                Expiration
            direction (str):
                Buy or Sell.
            total_received (Union[Dict[str, str], str]):
                Amount received. Defaults to None.
            total_paid (Union[Dict[str, str], str]):
                Costs account (str): Account.
            account (str):
                Accounts address.
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


def _parse_currency_amount(currency_amount: Union[str, FieldName]) -> AccountBalance:
    """Parses an accounts balance and formats it into a standard format.

    Args:
        currency_amount (Union[str, FieldName]):
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
        counterparty=currency_amount.issuer,
        value=currency_amount.value,
    )


def _calculate_delta(
    final_amount: Union[AccountBalance, None],
    previous_amount: Union[AccountBalance, None],
) -> Union[Decimal, int]:
    if isinstance(final_amount, AccountBalance) and isinstance(
        previous_amount, AccountBalance
    ):
        previous_value = Decimal(previous_amount.value)
        return 0 - previous_value

    return 0


def _parse_order_status(
    node: NormalizedNode,
) -> Union[Literal["created", "partially-filled", "filled", "cancelled"], None]:
    """Parses the status of an order.

    Returns:
        Union[Literal['created', 'partially-filled', 'filled', 'cancelled'], None]:
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
) -> Union[AccountBalance, ChangeAmount, None]:
    """Parse the changed amount of an order.

    Args:
        node (NormalizedNode):
            Normalized node.
        side (Literal['TakerPays', 'TakerGets']):
            Side of the order to parse.

    Returns:
        Union[AccountBalance, ChangeAmount, None:
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
        taker_gets = node.final_fields.TakerGets
        taker_pays = node.final_fields.TakerPays
    elif node.new_fields is not None:
        taker_gets = node.new_fields.TakerGets
        taker_pays = node.new_fields.TakerPays
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


def _get_expiration_time(node: NormalizedNode) -> Union[str, None]:
    """Formats the ripple timestamp to a easy to read format.

    Args:
        node (NormalizedNode): Normalized node.

    Returns:
        Union[str, None]:
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
    taker_gets: Union[Dict[str, str], str],
    taker_pays: Union[Dict[str, str], str],
    direction: Literal["sell", "buy"],
) -> Tuple[Union[Dict[str, str], str], Union[Dict[str, str], str]]:
    """Calculate what the taker had to pay and what he received.

    Args:
        taker_gets (Union[Dict[str, str], str]):
            TakerGets amount.
        taker_pays (Union[Dict[str, str], str]):
            TakerPays amount.
        direction (Literal["buy", "sell"]):
            'buy' or 'sell' offer.

    Returns:
        Tuple[Union[Dict[str, str], str], Union[Dict[str, str], str]]:
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
        Dict[str, Union[ Dict[str, str], bool, int, str ]]:
            A order book change.
    """
    if node.final_fields is not None:
        seq = node.final_fields.Sequence
    elif node.new_fields is not None:
        seq = node.new_fields.Sequence

    if node.final_fields is not None:
        sell = node.final_fields.Flags & lfs_sell != 0
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


def parse_order_book_changes(
    nodes: List[NormalizedNode],
) -> List[Dict[str, Union[Dict[str, str], bool, int, str]]]:
    """Filter nodes by 'EntryType': 'Offer'.

    Args:
        nodes (List[NormalizedNode]): Affected nodes.

    Returns:
        List[Dict[str, Union[Dict[str, str], bool, int, str]]]:
            A list of all nodes with 'EntryType': 'Offer'
    """
    filter_nodes = map_(
        filter_(nodes, lambda node: True if node.entry_type == "Offer" else False),
        _parse_order_change,
    )

    return filter_nodes  # type: ignore
