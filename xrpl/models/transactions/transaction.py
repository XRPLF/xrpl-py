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

STR_TO_TRANSACTION_DICT = {}


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
        return {**super().to_dict(), "transaction_type": self.transaction_type.value}

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

    @classmethod
    def get_transaction_type(cls: Transaction, transaction_type: str) -> Transaction:
        """
        Returns the correct transaction type based on the string name.

        Args:
            transaction_type: The String name of the Transaction object.

        Returns:
            The transaction class with the given name.
        """
        if transaction_type == "AccountDelete":
            from xrpl.models.transactions import AccountDelete

            return AccountDelete
        elif transaction_type == "AccountSet":
            from xrpl.models.transactions import AccountSet

            return AccountSet
        elif transaction_type == "CheckCancel":
            from xrpl.models.transactions import CheckCancel

            return CheckCancel
        elif transaction_type == "CheckCash":
            from xrpl.models.transactions import CheckCash

            return CheckCash
        elif transaction_type == "CheckCreate":
            from xrpl.models.transactions import CheckCreate

            return CheckCreate
        elif transaction_type == "DepositPreauth":
            from xrpl.models.transactions import DepositPreauth

            return DepositPreauth
        elif transaction_type == "EscrowCancel":
            from xrpl.models.transactions import EscrowCancel

            return EscrowCancel
        elif transaction_type == "EscrowCreate":
            from xrpl.models.transactions import EscrowCreate

            return EscrowCreate
        elif transaction_type == "EscrowFinish":
            from xrpl.models.transactions import EscrowFinish

            return EscrowFinish
        elif transaction_type == "OfferCancel":
            from xrpl.models.transactions import OfferCancel

            return OfferCancel
        elif transaction_type == "OfferCreate":
            from xrpl.models.transactions import OfferCreate

            return OfferCreate
        elif transaction_type == "Payment":
            from xrpl.models.transactions import Payment

            return Payment
        elif transaction_type == "PaymentChannelClaim":
            from xrpl.models.transactions import PaymentChannelClaim

            return PaymentChannelClaim
        elif transaction_type == "PaymentChannelCreate":
            from xrpl.models.transactions import PaymentChannelCreate

            return PaymentChannelCreate
        elif transaction_type == "PaymentChannelFund":
            from xrpl.models.transactions import PaymentChannelFund

            return PaymentChannelFund
        elif transaction_type == "SetRegularKey":
            from xrpl.models.transactions import SetRegularKey

            return SetRegularKey
        elif transaction_type == "SignerListSet":
            from xrpl.models.transactions import SignerListSet

            return SignerListSet
        elif transaction_type == "TrustSet":
            from xrpl.models.transactions import TrustSet

            return TrustSet
