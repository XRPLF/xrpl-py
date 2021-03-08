"""
The base class for all transaction types. Represents fields common to all transaction
types.

See https://xrpl.org/transaction-types.html.
See https://xrpl.org/transaction-common-fields.html.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from xrpl.models.base_model import BaseModel
from xrpl.models.required import REQUIRED


class TransactionType(str, Enum):
    """Enum containing the different Transaction types."""

    AccountDelete = "AccountDelete"
    AccountSet = "AccountSet"
    CheckCancel = "CheckCancel"
    CheckCash = "CheckCash"
    CheckCreate = "CheckCreate"
    DepositPreauth = "DepositPreauth"
    EscrowCancel = "EscrowCancel"
    EscrowCreate = "EscrowCreate"
    EscrowFinish = "EscrowFinish"
    OfferCancel = "OfferCancel"
    OfferCreate = "OfferCreate"
    Payment = "Payment"
    PaymentChannelClaim = "PaymentChannelClaim"
    PaymentChannelCreate = "PaymentChannelCreate"
    PaymentChannelFund = "PaymentChannelFund"
    SetRegularKey = "SetRegularKey"
    SignerListSet = "SignerListSet"
    TrustSet = "TrustSet"


@dataclass(frozen=True)
class Transaction(BaseModel):
    """
    The base class for all transaction types. Represents fields common to all
    transaction types.

    See https://xrpl.org/transaction-types.html.
    See https://xrpl.org/transaction-common-fields.html.
    """

    account: str = REQUIRED
    transaction_type: TransactionType = REQUIRED
    fee: Optional[str] = None  # auto-fillable
    sequence: Optional[int] = None  # auto-fillable
    account_txn_id: Optional[str] = None
    flags: int = 0
    last_ledger_sequence: Optional[int] = None
    # TODO make type
    memos: Optional[List[Any]] = None
    # TODO make type
    signers: Optional[List[Any]] = None
    source_tag: Optional[int] = None
    signing_pub_key: Optional[str] = None
    txn_signature: Optional[str] = None

    def to_dict(self: Transaction) -> Dict[str, Any]:
        """
        Returns the dictionary representation of a Transaction.

        Returns:
            The dictionary representation of a Transaction.
        """
        return {**super().to_dict(), "transaction_type": self.transaction_type.name}

    def has_flag(self: Transaction, flag: int) -> bool:
        """
        Returns whether the transaction has the given flag value set.

        Args:
            flag: The given flag value for which the function will determine whether it
                is set.

        Returns:
            Whether the transaction has the given flag value set.
        """
        return self.flags & flag != 0
