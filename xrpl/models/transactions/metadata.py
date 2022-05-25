"""Models for a transaction's metadata."""

from typing import Dict, List, Optional, Union

from typing_extensions import Literal, TypedDict

from xrpl.models.amounts.amount import Amount


class Fields(TypedDict, total=False):
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


class OptionalModifiedNodeFields(TypedDict, total=False):
    """The optional fields of `ModifiedNodeFields`."""

    """
    The fields are separated from `ModifiedNodeFields` to make them optional,
    while keeping `LedgerEntryType` and `LedgerIndex` required.
    """

    FinalFields: Optional[Fields]
    PreviousFields: Optional[Fields]
    PreviousTxnID: Optional[str]
    PreviousTxnLgrSeq: Optional[int]


class ModifiedNodeFields(OptionalModifiedNodeFields):
    """Fields of a ModifiedNode."""

    LedgerEntryType: str
    LedgerIndex: str


class ModifiedNode(TypedDict):
    """ModifiedNode model."""

    ModifiedNode: ModifiedNodeFields


class OptionalDeletedNodeFields(TypedDict, total=False):
    """The optional fields of `DeletedNodeFields`."""

    """
    The fields are separated from `DeletedNodeFields` to make them optional,
    while keeping `LedgerEntryType`, `LedgerIndex` and `FinalFields` required.
    """

    PreviousFields: Optional[Fields]


class DeletedNodeFields(OptionalDeletedNodeFields):
    """Fields of a DeletedNode."""

    LedgerEntryType: str
    LedgerIndex: str
    FinalFields: Fields


class DeletedNode(TypedDict):
    """DeletedNode model."""

    DeletedNode: DeletedNodeFields


class OptionalTransactionMetadataFields(TypedDict, total=False):
    """The optional fields of `TransactionMetadata`."""

    """
    The fields are separated from `TransactionMetadata` to make them optional,
    while keeping `AffectedNodes`, `TransactionIndex` and `TransactionResult` required.
    """

    DeliveredAmount: Optional[Amount]
    # "unavailable" possible for transactions before 2014-01-20
    delivered_amount: Optional[Union[Amount, Literal["unavailable"]]]


class TransactionMetadata(OptionalTransactionMetadataFields):
    """A model for a transaction's metadata."""

    AffectedNodes: List[Union[CreatedNode, ModifiedNode, DeletedNode]]
    TransactionIndex: int
    TransactionResult: str
