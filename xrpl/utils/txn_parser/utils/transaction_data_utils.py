"""Helper functions to format raw transaction data."""

from __future__ import annotations

from typing import Any, Dict, List, Union, cast

from pydash import map_  # type: ignore
from typing_extensions import Literal

from xrpl.utils.txn_parser.utils.types import (
    AccountBalance,
    NormalizedFields,
    NormalizedNode,
    RawTxnType,
    SubscriptionRawTxnType,
    XRPLTxnFieldsException,
)


def validate_transaction_fields(
    transaction_data: Union[RawTxnType, SubscriptionRawTxnType],
) -> None:
    """Check if the transaction fields are valid.

    Args:
        transaction_data (Union[RawTxnType, SubscriptionRawTxnType]):
            The raw transaction data.

    Raises:
        XRPLTxnFieldsException: If the raw transaction data is malformed.
    """
    if "transaction" in transaction_data:
        if "Account" not in transaction_data["transaction"]:  # type: ignore
            raise XRPLTxnFieldsException(
                "Malformed transaction fields: Transaction"
                "field 'Account' must be included."
            )
    elif "Account" not in transaction_data:
        raise XRPLTxnFieldsException(
            "Malformed transaction fields: Transaction"
            "field 'Account' must be included."
        )

    if "meta" not in transaction_data:
        raise XRPLTxnFieldsException(
            "Malformed transaction fields: Transaction field 'meta' must be included."
        )

    meta = transaction_data["meta"]
    if "AffectedNodes" not in meta or not meta["AffectedNodes"]:
        raise XRPLTxnFieldsException("Malformed transaction fields: No nodes provided.")


def normalize_transaction(
    transaction_data: SubscriptionRawTxnType,
) -> RawTxnType:
    """Formats the raw transaction data into one standard format.

    Args:
        transaction_data (SubscriptionRawTxnType):
            The raw transaction data.

    Returns:
        Transaction data in standard format.
    """
    transaction = transaction_data["transaction"]
    normalized_txn = {
        tx_field_name: tx_field_value
        for tx_field_name, tx_field_value in transaction.items()
    }

    meta = transaction_data["meta"]
    normalized_txn["meta"] = meta
    ledger_index = transaction_data["ledger_index"]
    normalized_txn["ledger_index"] = ledger_index

    return cast(RawTxnType, normalized_txn)


def normalize_fields(
    fields: Dict[str, Any],
) -> NormalizedFields:
    """Normalize 'NewFields', 'FinalFields' and 'ModifiedFields'.

    Args:
        fields (Dict[str, Any):
            A dictionary of all fields that field state has.
            E.g.: {'Balance': '62537659', 'OwnerCount': 16, 'Sequence': 67702065}

    Returns:
        NormalizedFields:
            The full field state with all its fields as objects.
    """
    balance = fields["Balance"] if "Balance" in fields else None
    low_limit = fields["LowLimit"] if "LowLimit" in fields else None
    high_limit = fields["HighLimit"] if "HighLimit" in fields else None
    taker_gets = fields["TakerGets"] if "TakerGets" in fields else None
    taker_pays = fields["TakerPays"] if "TakerPays" in fields else None
    account = cast(str, fields["Account"]) if "Account" in fields else None
    sequence = cast(int, fields["Sequence"]) if "Sequence" in fields else None
    flags = cast(int, fields["Flags"]) if "Flags" in fields else None
    expiration = cast(int, fields["Expiration"]) if "Expiration" in fields else None

    field_state = NormalizedFields(
        Balance=AccountBalance(
            counterparty=balance["issuer"],
            currency=balance["currency"],
            value=balance["value"],
        )
        if isinstance(balance, dict)
        else balance,
        LowLimit=AccountBalance(
            counterparty=low_limit["issuer"],
            currency=low_limit["currency"],
            value=low_limit["value"],
        )
        if isinstance(low_limit, dict)
        else low_limit,
        HighLimit=AccountBalance(
            counterparty=high_limit["issuer"],
            currency=high_limit["currency"],
            value=high_limit["value"],
        )
        if isinstance(high_limit, dict)
        else high_limit,
        TakerGets=AccountBalance(
            counterparty=taker_gets["issuer"],
            currency=taker_gets["currency"],
            value=taker_gets["value"],
        )
        if isinstance(taker_gets, dict)
        else taker_gets,
        TakerPays=AccountBalance(
            counterparty=taker_pays["issuer"],
            currency=taker_pays["currency"],
            value=taker_pays["value"],
        )
        if isinstance(taker_pays, dict)
        else taker_pays,
        Account=account,
        Sequence=sequence,
        Flags=flags,
        Expiration=expiration,
    )

    return field_state


def normalize_node(affected_node: Dict[str, Any]) -> NormalizedNode:
    """Affected node to a standard format.

    Args:
        affected_node (Dict[str, Dict[str, Union[str, int,
        Dict[str, Union[str, int, Dict[str, str]]]]]]):
            Affected node.

    Returns:
        NormalizedNode:
            NormalizedNode object.
    """
    diff_type = cast(
        Literal["ModifiedNode", "CreatedNode", "DeletedNode"],
        list(affected_node.keys())[0],
    )
    node_fields = list(affected_node.values())[0]

    ledger_entry_type = str(node_fields["LedgerEntryType"])
    ledger_index = str(node_fields["LedgerIndex"])

    new_fields = None
    if "NewFields" in node_fields:
        new_fields = normalize_fields(fields=node_fields["NewFields"])

    final_fields = None
    if "FinalFields" in node_fields:
        final_fields = normalize_fields(fields=node_fields["FinalFields"])

    previous_fields = None
    if "PreviousFields" in node_fields:
        previous_fields = normalize_fields(fields=node_fields["PreviousFields"])

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
    transaction_data: Union[RawTxnType, SubscriptionRawTxnType]
) -> List[NormalizedNode]:
    """Normalize nodes.

    Args:
        transaction_data (Union[RawTxnType, SubscriptionRawTxnType]):
            Transactions raw data.

    Returns:
        List[NormalizedNode]: The normalized nodes
    """
    meta = transaction_data["meta"]
    if isinstance(meta, dict):
        affected_nodes = meta["AffectedNodes"]
        if not affected_nodes:
            return []
        return map_(affected_nodes, normalize_node)  # type: ignore
    else:
        return []
