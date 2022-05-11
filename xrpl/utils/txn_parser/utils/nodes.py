"""Helper functions to normalize an affected node."""

from typing import List, Union

from typing_extensions import TypedDict

from xrpl.models import (
    Amount,
    CreatedNode,
    DeletedNode,
    IssuedCurrencyAmount,
    ModifiedNode,
    TransactionMetadata,
)


class Fields(TypedDict):
    """Model for possible fields."""

    Account: str
    Balance: Amount
    LowLimit: IssuedCurrencyAmount
    HighLimit: IssuedCurrencyAmount


class NormalizedNode(TypedDict):
    """A model representing an affected node in a standard format."""

    NodeType: str
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
    diff_type = list(affected_node.keys())[0]
    node = affected_node[diff_type]
    return NormalizedNode(NodeType=diff_type, **node)


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
