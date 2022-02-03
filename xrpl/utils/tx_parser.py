"""
Parse balance changes and final balances of every
account involved in the given transaction.
"""

from typing import Any, Dict, Iterable, List, Union

from pydash import compact, flatten, group_by, is_empty, map_, map_values

from xrpl.constants import XRPLException
from xrpl.utils.xrp_conversions import drops_to_xrp


class XRPLMetadataException(XRPLException):
    """Exception for invalid transaction metadata."""

    pass


def _is_valid_metadata(metadata: Dict[str, Any]) -> None:
    if "Account" not in metadata:
        raise XRPLMetadataException(
            "Metadata incomplete: Metadata field 'Account' must be included."
        )

    if "meta" not in metadata:
        raise XRPLMetadataException(
            "Metadata incomplete: Metadata field 'meta' must be included."
        )

    if "AffectedNodes" not in metadata["meta"] or not metadata["meta"]["AffectedNodes"]:
        raise XRPLMetadataException("Metadata incomplete: No nodes provided.")


class _NormalizedNode:
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


def _normalize_node(affectedNode: Dict[str, Any]) -> _NormalizedNode:
    diff_type = list(affectedNode)[0]
    node = affectedNode[diff_type]

    n = _NormalizedNode(
        diffType=diff_type,
        entryType=node["LedgerEntryType"],
        ledgerIndex=node["LedgerIndex"],
        newFields=node["NewFields"] if "NewFields" in node else {},
        finalFields=node["FinalFields"] if "FinalFields" in node else {},
        previousFields=node["PreviousFields"] if "PreviousFields" in node else {},
    )

    return n


def _normalize_nodes(metadata: Dict[str, Any]) -> Iterable[_NormalizedNode]:
    affected_nodes = metadata["meta"]["AffectedNodes"]
    if not affected_nodes:
        return []

    return map(_normalize_node, affected_nodes)


class _Balance:
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


class _TrustLineQuantity:
    """Trust line quantity."""

    def __init__(self: Any, address: str, balance: Dict[str, str]) -> None:
        """
        Args:
            address (str): Address
            balance (Dict[str, str]): Balance
        """
        self.address = address
        self.balance = _Balance(
            counterparty=balance["counterparty"],
            currency=balance["currency"],
            value=balance["value"],
        )


def _group_by_address(balanceChanges: Any) -> Any:
    grouped = group_by(balanceChanges, lambda node: node.address)

    return map_values(grouped, lambda group: map_(group, lambda node: node.balance))


def _parse_value(value: Any) -> float:
    if "value" in value:
        return float(value["value"])
    else:
        return float(value)


def _compute_balance_changes(node: _NormalizedNode) -> Union[None, int, float]:
    value = None
    if "Balance" in node.new_fields:
        value = _parse_value(node.new_fields["Balance"])
    elif "Balance" in node.previous_fields and "Balance" in node.final_fields:
        value = _parse_value(node.final_fields["Balance"]) - _parse_value(
            node.previous_fields["Balance"]
        )

    return None if value is None else None if value == 0 else value


def _parse_final_balance(node: _NormalizedNode) -> Union[float, None]:
    if "Balance" in node.new_fields:
        return _parse_value(node.new_fields["Balance"])
    elif "Balance" in node.final_fields:
        return _parse_value(node.final_fields["Balance"])

    return None


def _parse_xrp_quantity(
    node: _NormalizedNode,
    valueParser: Any,
) -> Union[_TrustLineQuantity, None]:
    value = valueParser(node)
    if value is None:
        return None
    is_negative = False
    if str(value).startswith("-"):
        is_negative = True
    result = _TrustLineQuantity(
        address=node.final_fields["Account"]
        if node.final_fields
        else node.new_fields["Account"],
        balance={
            "counterparty": "",
            "currency": "XRP",
            "value": str(drops_to_xrp(str(abs(int(value)))))
            if not is_negative
            else "-{}".format(drops_to_xrp(str(abs(int(value))))),
        },
    )

    return result


def _flip_trustline_perspective(quantity: _TrustLineQuantity) -> _TrustLineQuantity:
    negated_balance = abs(float(quantity.balance.value))
    result = _TrustLineQuantity(
        address=quantity.balance.counterparty,
        balance={
            "counterparty": quantity.address,
            "currency": quantity.balance.currency,
            "value": str(negated_balance),
        },
    )

    return result


def _parse_trustline_quantity(
    node: _NormalizedNode,
    valueParser: Any,
) -> Union[None, List[_TrustLineQuantity]]:
    value = valueParser(node)
    if value is None:
        return None
    fields = node.final_fields if is_empty(node.new_fields) else node.new_fields
    result = _TrustLineQuantity(
        address=fields["LowLimit"]["issuer"],
        balance={
            "counterparty": fields["HighLimit"]["issuer"],
            "currency": fields["Balance"]["currency"],
            "value": str(value),
        },
    )

    return [result, _flip_trustline_perspective(result)]


def _parse_quantities(
    metadata: Dict[str, Union[str, int, bool, Dict[str, Any]]], valueParser: Any
) -> Any:
    values: List[Any] = []
    for node in _normalize_nodes(metadata=metadata):
        if node.entry_type == "AccountRoot":
            values.append(_parse_xrp_quantity(node, valueParser))
        elif node.entry_type == "RippleState":
            values.append(_parse_trustline_quantity(node, valueParser))
        else:
            values.append([])

    return _group_by_address(compact(flatten(values)))


def parse_balance_changes(
    metadata: Dict[str, Union[str, int, bool, Dict[str, Any]]]
) -> Dict[str, List[Dict[str, str]]]:
    """Parse the balance changes of all accounts affected
    by the transaction after it occurred.

    Args:
        metadata (Dict[str, Union[str, int, bool, Dict[str, Any]]]):
            Transaction metadata including the account that
            sent the transaction and the affected nodes.

    Returns:
        Dict[str, List[Dict[str, str]]]:
            A dictionary of all accounts affected by the transaction and
            their list of currencies that balances got changed by it.
    """
    _is_valid_metadata(metadata=metadata)
    parsedQuantities = _parse_quantities(
        metadata=metadata, valueParser=_compute_balance_changes
    )
    result: Dict[str, List[Dict[str, str]]] = {}
    for k, v in parsedQuantities.items():
        address = k
        change = v
        result[address] = []
        for obj in change:
            if isinstance(obj.counterparty, tuple):
                obj.counterparty = obj.counterparty[0]
            result[address].append(
                {
                    "Counterparty": obj.counterparty,
                    "Currency": obj.currency,
                    "Value": obj.value,
                }
            )

    return result


def parse_final_balances(
    metadata: Dict[str, Union[str, int, bool, Dict[str, Any]]]
) -> Dict[str, List[Dict[str, str]]]:
    """Parse the final balances of all accounts affected
    by the transaction after it occurred.

    Args:
        metadata (Dict[str, Union[str, int, bool, Dict[str, Any]]]):
            Transaction metadata including the account that
            sent the transaction and the affected nodes.


    Returns:
        Dict[str, List[Dict[str, str]]]:
            A dictionary of all accounts affected by the transaction and
            their list of final currency amounts.
    """
    _is_valid_metadata(metadata=metadata)
    parsedQuantities = _parse_quantities(metadata, _parse_final_balance)

    result: Dict[str, List[Dict[str, str]]] = {}
    for k, v in parsedQuantities.items():
        address = k
        change = v
        result[address] = []
        for obj in change:
            if isinstance(obj.counterparty, tuple):
                obj.counterparty = obj.counterparty[0]
            result[address].append(
                {
                    "Counterparty": obj.counterparty,
                    "Currency": obj.currency,
                    "Value": obj.value,
                }
            )

    return result
