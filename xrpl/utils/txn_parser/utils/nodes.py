"""Helper functions to normalize an affected node."""

from typing import List, Union, cast

from typing_extensions import Literal, TypedDict

from xrpl.models import CreatedNode, DeletedNode, ModifiedNode, TransactionMetadata
from xrpl.utils.txn_parser.utils.types import BalanceType


class Fields(TypedDict):
    """Model for possible fields."""

    Account: str
    Balance: Union[BalanceType, str]
    LowLimit: BalanceType
    HighLimit: BalanceType


class NormalizedNode(TypedDict):
    """A model representing an affected node in a standard format."""

    NodeType: Literal["CreatedNode", "ModifiedNode", "DeletedNode"]
    LedgerEntryType: str
    LedgerIndex: str
    NewFields: Fields
    FinalFields: Fields
    PreviousFields: Fields
    PreviousTxnID: str
    PreviouTxnLgrSeq: int


def _normalize_node(
    affected_node: Union[CreatedNode, ModifiedNode, DeletedNode]
) -> NormalizedNode:
    diff_type = cast(
        Literal["CreatedNode", "ModifiedNode", "DeletedNode"],
        list(affected_node.keys())[0],
    )
    node = affected_node[diff_type]  # type: ignore
    return NormalizedNode(NodeType=diff_type, **node)  # type: ignore


def normalize_nodes(metadata: TransactionMetadata) -> List[NormalizedNode]:
    """
    Normalize all nodes of a transaction's metadata.

    Args:
        metadata: The transaction's metadata.

    Returns:
        The normalized nodes.
    """
    if len(metadata["AffectedNodes"]) == 0:
        return []
    return [_normalize_node(node) for node in metadata["AffectedNodes"]]
