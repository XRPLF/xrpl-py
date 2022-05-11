"""Helper functions to normalize an affected node."""

from typing import List, Optional, Union, cast

from typing_extensions import Literal, TypedDict

from xrpl.models import TransactionMetadata
from xrpl.models.transactions.metadata import CreatedNode, DeletedNode, ModifiedNode
from xrpl.utils.txn_parser.utils.types import BalanceType


class Fields(TypedDict):
    """Model for possible fields."""

    Account: Optional[str]
    Balance: Optional[Union[BalanceType, str]]
    LowLimit: Optional[BalanceType]
    HighLimit: Optional[BalanceType]


class NormalizedNode(TypedDict):
    """A model representing an affected node in a standard format."""

    NodeType: Literal["CreatedNode", "ModifiedNode", "DeletedNode"]
    LedgerEntryType: str
    LedgerIndex: str
    NewFields: Optional[Fields]
    FinalFields: Optional[Fields]
    PreviousFields: Optional[Fields]
    PreviousTxnID: Optional[str]
    PreviousTxnLgrSeq: Optional[int]


def _normalize_node(
    affected_node: Union[CreatedNode, ModifiedNode, DeletedNode]
) -> NormalizedNode:
    assert len(affected_node.keys()) == 1
    diff_type = cast(
        Literal["CreatedNode", "ModifiedNode", "DeletedNode"],
        list(affected_node.keys())[0],
    )
    node = affected_node[diff_type]  # type: ignore
    return NormalizedNode(
        NodeType=diff_type,
        LedgerEntryType=node["LedgerEntryType"],
        LedgerIndex=node["LedgerIndex"],
        NewFields=node.get("NewFields"),
        FinalFields=node.get("FinalFields"),
        PreviousFields=node.get("PreviousFields"),
        PreviousTxnID=node.get("PreviousTxnID"),
        PreviousTxnLgrSeq=node.get("PreviousTxnLgrSeq"),
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
