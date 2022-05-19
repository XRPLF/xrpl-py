"""Models for a transaction's metadata."""

from typing import Dict, List, Optional, Union

from typing_extensions import Literal, TypedDict

from xrpl.models.amounts.amount import Amount


class Fields(TypedDict):
    """Model for possible fields."""

    Account: Optional[str]
    LowLimit: Optional[Dict[str, str]]
    HighLimit: Optional[Dict[str, str]]
    Balance: Optional[Union[Dict[str, str], str]]


class CreatedNodeFields(TypedDict):
    """Fields of a CreatedNode."""

    LedgerEntryType: str
    LedgerIndex: str
    NewFields: Fields


class CreatedNode(TypedDict):
    """CreatedNode model."""

    CreatedNode: CreatedNodeFields


class ModifiedNodeFields(TypedDict):
    """Fields of a ModifiedNode."""

    LedgerEntryType: str
    LedgerIndex: str
    FinalFields: Optional[Fields]
    PreviousFields: Optional[Fields]
    PreviousTxnID: Optional[str]
    PreviousTxnLgrSeq: Optional[int]


class ModifiedNode(TypedDict):
    """ModifiedNode model."""

    ModifiedNode: ModifiedNodeFields


class DeletedNodeFields(TypedDict):
    """Fields of a DeletedNode."""

    LedgerEntryType: str
    LedgerIndex: str
    FinalFields: Fields
    PreviousFields: Optional[Fields]


class DeletedNode(TypedDict):
    """DeletedNode model."""

    DeletedNode: DeletedNodeFields


class TransactionMetadata(TypedDict):
    """A model for a transaction's metadata."""

    AffectedNodes: List[Union[CreatedNode, ModifiedNode, DeletedNode]]
    DeliveredAmount: Optional[Amount]
    # "unavailable" possible for transactions before 2014-01-20
    delivered_amount: Optional[Union[Amount, Literal["unavailable"]]]
    TransactionIndex: int
    TransactionResult: str
