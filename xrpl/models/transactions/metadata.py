"""Models for a transaction's metadata."""

from typing import Any, Dict, List, Union

from typing_extensions import Literal, TypedDict

from xrpl.models.amounts.amount import Amount


class CreatedNodeFields(TypedDict):
    """Fields of a CreatedNode."""

    LedgerEntryType: str
    LedgerIndex: str
    NewFields: Dict[str, Any]


class CreatedNode(TypedDict):
    """CreatedNode model."""

    CreatedNode: CreatedNodeFields


class ModifiedNodeFields(TypedDict):
    """Fields of a ModifiedNode."""

    LedgerEntryType: str
    LedgerIndex: str
    FinalFields: Dict[str, Any]
    PreviousFields: Dict[str, Any]
    PreviousTxnID: str
    PreviouTxnLgrSeq: int


class ModifiedNode(TypedDict):
    """ModifiedNode model."""

    ModifiedNode: ModifiedNodeFields


class DeletedNodeFields(TypedDict):
    """Fields of a DeletedNode."""

    LedgerEntryType: str
    LedgerIndex: str
    FinalFields: Dict[str, Any]


class DeletedNode(TypedDict):
    """DeletedNode model."""

    DeletedNode: DeletedNodeFields


class TransactionMetadata(TypedDict):
    """A model for a transaction's metadata."""

    AffectedNodes: List[Union[CreatedNode, ModifiedNode, DeletedNode]]
    DeliveredAmount: Amount
    # "unavailable" possible for transactions before 2014-01-20
    delivered_amount: Union[Amount, Literal["unavailable"]]
    TransactionIndex: int
    TransactionResult: str
