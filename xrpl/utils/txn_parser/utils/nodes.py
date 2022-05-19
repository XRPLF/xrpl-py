"""Helper functions to normalize an affected node."""

from typing import List, Optional, Union, cast

from typing_extensions import Literal, TypedDict

from xrpl.models import TransactionMetadata
from xrpl.models.transactions.metadata import (
    CreatedNode,
    DeletedNode,
    Fields,
    ModifiedNode,
)


class OptionalFieldNames(TypedDict, total=False):
    """The optional fields of `NormalizedNode`."""

    """
    The fields are separated from `NormalizedNode` to make it optional,
    while keeping `NodeType`, `LedgerEntryType` and `LedgerIndex` required.
    """

    NewFields: Optional[Fields]
    FinalFields: Optional[Fields]
    PreviousFields: Optional[Fields]
    PreviousTxnID: Optional[str]
    PreviousTxnLgrSeq: Optional[int]


class NormalizedNode(OptionalFieldNames):
    """A model representing an affected node in a standard format."""

    NodeType: Literal["CreatedNode", "ModifiedNode", "DeletedNode"]
    LedgerEntryType: str
    LedgerIndex: str


def _normalize_node(
    affected_node: Union[CreatedNode, ModifiedNode, DeletedNode]
) -> NormalizedNode:
    node_keys = affected_node.keys()
    assert len(node_keys) == 1
    diff_type = cast(
        Literal["CreatedNode", "ModifiedNode", "DeletedNode"],
        list(node_keys)[0],
    )
    created_node = None
    modified_node = None
    if diff_type == "CreatedNode":
        created_node = cast(CreatedNode, affected_node)["CreatedNode"]
    elif diff_type == "ModifiedNode":
        modified_node = cast(ModifiedNode, affected_node)["ModifiedNode"]
    else:
        deleted_node = cast(DeletedNode, affected_node)["DeletedNode"]
    node = (
        created_node
        if created_node is not None
        else modified_node
        if modified_node is not None
        else deleted_node
    )
    ledger_entry_type = node["LedgerEntryType"]
    ledger_index = node["LedgerIndex"]
    new_fields = cast(Optional[Fields], node.get("NewFields"))
    previous_fields = cast(Optional[Fields], node.get("PreviousFields"))
    final_fields = cast(Optional[Fields], node.get("FinalFields"))
    previous_txn_id = cast(Optional[str], node.get("PreviousTxnID"))
    previous_txn_lgr_seq = cast(Optional[int], node.get("PreviousTxnLgrSeq"))
    return NormalizedNode(
        NodeType=diff_type,
        LedgerEntryType=ledger_entry_type,
        LedgerIndex=ledger_index,
        NewFields=new_fields,
        PreviousFields=previous_fields,
        FinalFields=final_fields,
        PreviousTxnID=previous_txn_id,
        PreviousTxnLgrSeq=previous_txn_lgr_seq,
    )


def normalize_nodes(metadata: TransactionMetadata) -> List[NormalizedNode]:
    """
    Normalize all nodes of a transaction's metadata.

    Args:
        metadata: The transaction's metadata.

    Returns:
        The normalized nodes.
    """
    return [_normalize_node(node) for node in metadata["AffectedNodes"]]
