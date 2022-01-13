import pydash
from typing import Dict, List, Union
from xrpl.constants import XRPLException
from xrpl.utils.xrp_conversions import drops_to_xrp


class XRPLMetadataExcetion(XRPLException):
    """Exception for invalid transaction metadata."""

    pass


# Utils
def _is_valid_metadata(metadata: dict):
    if "Account" not in metadata:
        raise XRPLMetadataExcetion(
            "Metadata field 'Account' must be included."
        )

    if "meta" not in metadata:
        raise XRPLMetadataExcetion(
            "Metadata field 'meta' must be included."
        )

    if "AffectedNodes" not in metadata["meta"] or not metadata["meta"]["AffectedNodes"]:
        raise XRPLMetadataExcetion(
            "No nodes provided."
        )

    return True


class NormalizedNode():
    def __init__(
        self,
        diffType: str,
        entryType: str,
        ledgerIndex: str,
        newFields: dict,
        finalFields: dict,
        previousFields: dict
    ):
        self.diff_type = diffType
        self.entry_type = entryType
        self.ledger_index = ledgerIndex
        self.new_fields = newFields
        self.final_fields = finalFields
        self.previous_fields = previousFields


def _normalize_node(affectedNode: dict) -> NormalizedNode:
    diff_type = list(affectedNode)[0]
    node = affectedNode[diff_type]

    n = NormalizedNode(
        diffType=diff_type,
        entryType=node["LedgerEntryType"],
        ledgerIndex=node["LedgerIndex"],
        newFields=node["NewFields"] if "NewFields" in node else {},
        finalFields=node["FinalFields"] if "FinalFields" in node else {},
        previousFields=node["PreviousFields"] if "PreviousFields" in node else {}
    )

    return n


def _normalize_nodes(metadata: dict):
    affected_nodes = metadata["meta"]["AffectedNodes"]
    if not affected_nodes:
        return []

    return map(_normalize_node, affected_nodes)


class Balance():
    def __init__(self, counterparty: str, currency: str, value: str) -> None:
        self.counterparty = counterparty
        self.currency = currency
        self.value = value


class TrustLineQuantity():
    def __init__(self, address: str, balance: dict) -> None:
        self.address = address,
        self.balance = Balance(
            counterparty=balance["counterparty"],
            currency=balance["currency"],
            value=balance["value"]
        )
###############


def _group_by_address(balanceChanges: list) -> Dict[str, Balance]:
    grouped = pydash.group_by(balanceChanges, lambda node: node.address)

    return pydash.map_values(
        grouped,
        lambda group: pydash.map_(group, lambda node: node.balance)
    )


def _parse_value(value) -> float:
    if "value" in value:
        return float(value["value"])
    else:
        return float(value)


def _compute_balance_changes(node: NormalizedNode) -> float:
    value = None
    if "Balance" in node.new_fields:
        value = _parse_value(node.new_fields["Balance"])
    elif "Balance" in node.previous_fields and "Balance" in node.final_fields:
        value = _parse_value(
            node.final_fields["Balance"]
        ) - _parse_value(
            node.previous_fields["Balance"]
        )

    return None if value is None else None if value == 0 else value


def _parse_final_balance(node: NormalizedNode) -> float:
    if "Balance" in node.new_fields:
        return _parse_value(node.new_fields["Balance"])
    elif "Balance" in node.final_fields:
        return _parse_value(node.final_fields["Balance"])

    return None


def _parse_xrp_quantity(
    node: NormalizedNode,
    valueParser: Union[_compute_balance_changes, _parse_final_balance]
) -> Union[TrustLineQuantity, None]:
    value = valueParser(node)
    if value is None:
        return None
    is_negative = False
    if str(value).startswith("-"):
        is_negative = True
    result = TrustLineQuantity(
        address=node.final_fields["Account"]
        if node.final_fields
        else node.new_fields["Account"],
        balance={
            "counterparty": "",
            "currency": "XRP",
            "value": str(drops_to_xrp(
                str(abs(int(value))))
            ) if not is_negative else "-{}".format(
                drops_to_xrp(str(abs(int(value))))
            )
        }
    )

    return result


def _flip_trustline_perspective(quantity: TrustLineQuantity) -> TrustLineQuantity:
    negated_balance = abs(float(quantity.balance.value))
    result = TrustLineQuantity(
        address=quantity.balance.counterparty,
        balance={
            "counterparty": quantity.address,
            "currency": quantity.balance.currency,
            "value": negated_balance
        }
    )

    return result


def _parse_trustline_quantity(
    node: NormalizedNode,
    valueParser: Union[_compute_balance_changes, _parse_final_balance]
) -> List[TrustLineQuantity]:
    value = valueParser(node)
    if value is None:
        return None
    fields = node.final_fields if pydash.is_empty(node.new_fields) else node.new_fields
    result = TrustLineQuantity(
        address=fields["LowLimit"]["issuer"],
        balance={
            "counterparty": fields["HighLimit"]["issuer"],
            "currency": fields["Balance"]["currency"],
            "value": str(value)
        }
    )

    return [result, _flip_trustline_perspective(result)]


def _parse_quantities(
    metadata: dict,
    valueParser: Union[_compute_balance_changes, _parse_final_balance]
) -> Dict[str, List[Balance]]:
    values = []
    for node in _normalize_nodes(metadata=metadata):
        if node.entry_type == "AccountRoot":
            values.append(_parse_xrp_quantity(node, valueParser))
        elif node.entry_type == "RippleState":
            values.append(_parse_trustline_quantity(node, valueParser))
        else:
            values.append([])

    return _group_by_address(pydash.compact(pydash.flatten(values)))


def parse_balance_changes(metadata: dict) -> Dict[str, List[Dict[str, str]]]:
    """Parse the balance changes of all accounts affected
    by the transaction after it occurred.

    Args:
        metadata (dict): Transaction metadata.

    Returns:
        Dict[str, List[Dict[str, str]]]:
        A dictionary of all accounts affected by the transaction and their list of
        currencies that balances got changed by it.
    """
    _is_valid_metadata(metadata=metadata)
    parsedQuantities = _parse_quantities(
        metadata=metadata,
        valueParser=_compute_balance_changes
    )
    result = {}
    for k, v in parsedQuantities.items():
        address = k[0]
        change = v
        result[address] = []
        for obj in change:
            if isinstance(obj.counterparty, tuple):
                obj.counterparty = obj.counterparty[0]
            result[address].append(
                {
                    "Counterparty": obj.counterparty,
                    "Currency": obj.currency,
                    "Value": obj.value
                }
            )

    return result


def parse_final_balances(metadata: dict) -> Dict[str, List[Dict[str, str]]]:
    """Parse the final balances of all accounts affected
    by the transaction after it occurred.

    Args:
        metadata (dict): Transaction metadata.

    Returns:
        Dict[str, List[Dict[str, str]]]:
        A dictionary of all accounts affected by the transaction and their list of
        final currency amounts.
    """
    _is_valid_metadata(metadata=metadata)
    parsedQuantities = _parse_quantities(metadata, _parse_final_balance)

    result = {}
    for k, v in parsedQuantities.items():
        address = k[0]
        change = v
        result[address] = []
        for obj in change:
            if isinstance(obj.counterparty, tuple):
                obj.counterparty = obj.counterparty[0]
            result[address].append(
                {
                    "Counterparty": obj.counterparty,
                    "Currency": obj.currency,
                    "Value": obj.value
                }
            )

    return result
