"""Types for the transaction parser."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Union

from typing_extensions import Literal, TypedDict

from xrpl.constants import XRPLException

CURRENCY_AMOUNT_TYPE = Union[Dict[str, str], str]


class MetaDataType(TypedDict):
    """Transaction metadata."""

    AffectedNodes: List[
        Dict[
            str,
            Dict[
                str,
                Union[str, int, Dict[str, Union[str, int, Dict[str, str]]]],
            ],
        ],
    ]
    TransactionIndex: int
    TransactionResult: str
    delivered_amount: CURRENCY_AMOUNT_TYPE


class TransactionFieldsType(TypedDict):
    """Transaction fields. Since this can represent fields from
    all transaction types, only common fields are defined.
    """

    Account: str
    TransactionType: str
    Fee: str
    Sequence: int
    Flags: int


class RawTxnType(TransactionFieldsType):
    """Raw transaction data received from a tx method."""

    meta: MetaDataType


class SubscriptionRawTxnType(TypedDict):
    """Raw transaction data received from a subscribtion method."""

    ledger_index: int
    meta: MetaDataType
    transaction: TransactionFieldsType


@dataclass
class NormalizedFields:
    """NormalizedFields"""

    Balance: Optional[Union[AccountBalance, str]] = None
    LowLimit: Optional[Union[AccountBalance, str]] = None
    HighLimit: Optional[Union[AccountBalance, str]] = None
    TakerGets: Optional[Union[AccountBalance, str]] = None
    TakerPays: Optional[Union[AccountBalance, str]] = None
    Account: Optional[str] = None
    Sequence: Optional[int] = None
    Flags: Optional[int] = None
    Expiration: Optional[Union[int, str]] = None


@dataclass
class NormalizedNode:
    """A standard format for nodes."""

    diff_type: Literal["ModifiedNode", "CreatedNode", "DeletedNode"]
    """Node type (ModifiedNode, CreatedNode or DeletedNode)"""
    entry_type: str
    """Entry type (e.g. Offer, AccountRoot, …)."""
    ledger_index: str
    """Ledger index."""
    new_fields: Optional[NormalizedFields] = None
    """New fields created by the transcation."""
    final_fields: Optional[NormalizedFields] = None
    """Fields after the transaction occurred."""
    previous_fields: Optional[NormalizedFields] = None
    """Fields before the transaction occurred."""


@dataclass
class AccountBalance:
    """A accounts balance."""

    counterparty: str
    """Counterparty"""
    currency: str
    """Currency"""
    value: str
    """Value"""


class XRPLTxnFieldsException(XRPLException):
    """Exception for invalid raw transaction data."""

    pass
