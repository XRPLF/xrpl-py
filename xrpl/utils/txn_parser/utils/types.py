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
    """A standard format for nodes.

    Args:
        diffType (str): Node type (ModifiedNode, CreatedNode or DeletedNode).
        entryType (str): Entry type (e.g. Offer, AccountRoot, …).
        ledgerIndex (str): Ledger index.
        newFields (Optional[NormalizedFields]):
            New fields.
        finalFields (Optional[NormalizedFields]):
            Fields after the transaction occurred.
        previousFields (Optional[NormalizedFields]):
            Fields before the transaction occurred.
    """

    diff_type: Literal["ModifiedNode", "CreatedNode", "DeletedNode"]
    entry_type: str
    ledger_index: str
    new_fields: Optional[NormalizedFields] = None
    final_fields: Optional[NormalizedFields] = None
    previous_fields: Optional[NormalizedFields] = None


@dataclass
class AccountBalance:
    """A accounts balance.

    Args:
        counterparty (str):
            Counterparty
        currency (str):
            Currency
        value (str):
            Value
    """

    counterparty: str
    currency: str
    value: str


class XRPLTxnFieldsException(XRPLException):
    """Exception for invalid raw transaction data."""

    pass
