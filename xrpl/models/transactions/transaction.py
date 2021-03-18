"""
The base class for all transaction types. Represents fields common to all transaction
types.

See https://xrpl.org/transaction-types.html.
See https://xrpl.org/transaction-common-fields.html.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Type, cast

from xrpl.models.base_model import BaseModel
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


class TransactionType(str, Enum):
    """Enum containing the different Transaction types."""

    ACCOUNT_DELETE = "AccountDelete"
    ACCOUNT_SET = "AccountSet"
    CHECK_CANCEL = "CheckCancel"
    CHECK_CASH = "CheckCash"
    CHECK_CREATE = "CheckCreate"
    DEPOSIT_PREAUTH = "DepositPreauth"
    ESCROW_CANCEL = "EscrowCancel"
    ESCROW_CREATE = "EscrowCreate"
    ESCROW_FINISH = "EscrowFinish"
    OFFER_CANCEL = "OfferCancel"
    OFFER_CREATE = "OfferCreate"
    PAYMENT = "Payment"
    PAYMENT_CHANNEL_CLAIM = "PaymentChannelClaim"
    PAYMENT_CHANNEL_CREATE = "PaymentChannelCreate"
    PAYMENT_CHANNEL_FUND = "PaymentChannelFund"
    SET_REGULAR_KEY = "SetRegularKey"
    SIGNER_LIST_SET = "SignerListSet"
    TRUST_SET = "TrustSet"


@require_kwargs_on_init
@dataclass(frozen=True)
class Memo(BaseModel):
    """
    The Memos field includes arbitrary messaging data with
    the transaction. It is presented as an array of objects.
    Each object has only one field, Memo, which in turn contains
    another object with one or more of the following fields.
    """

    memo_data: Optional[str] = None
    memo_format: Optional[str] = None
    memo_type: Optional[str] = None

    def _get_errors(self: Memo) -> Dict[str, str]:
        errors = super()._get_errors()
        present_memo_fields = [
            field
            for field in [
                self.memo_data,
                self.memo_format,
                self.memo_type,
            ]
            if field is not None
        ]
        if len(present_memo_fields) < 1:
            errors["Memo"] = "Memo must contain at least one field"
        return errors


@require_kwargs_on_init
@dataclass(frozen=True)
class Signer(BaseModel):
    """
    The Signers field contains a multi-signature, which has
    signatures from up to 8 key pairs, that together should
    authorize the transaction. The Signers list is an array
    of objects, each with one field, Signer. The Signer field
    has the following nested fields.
    """

    account: str = REQUIRED  # type: ignore
    txn_signature: str = REQUIRED  # type: ignore
    signing_pub_key: str = REQUIRED  # type: ignore


@require_kwargs_on_init
@dataclass(frozen=True)
class Transaction(BaseModel):
    """
    The base class for all transaction types. Represents fields common to all
    transaction types.

    See https://xrpl.org/transaction-types.html.
    See https://xrpl.org/transaction-common-fields.html.
    """

    account: str = REQUIRED  # type: ignore
    transaction_type: TransactionType = REQUIRED  # type: ignore
    fee: Optional[str] = None  # auto-fillable
    sequence: Optional[int] = None  # auto-fillable
    account_txn_id: Optional[str] = None
    flags: int = 0
    last_ledger_sequence: Optional[int] = None
    memos: Optional[List[Memo]] = None
    signers: Optional[List[Signer]] = None
    source_tag: Optional[int] = None
    signing_pub_key: Optional[str] = None
    txn_signature: Optional[str] = None

    def to_dict(self: Transaction) -> Dict[str, Any]:
        """
        Returns the dictionary representation of a Transaction.

        Returns:
            The dictionary representation of a Transaction.
        """
        # we need to override this because transaction_type is using `field`
        # which will not include the value in the objects __dict__
        return {**super().to_dict(), "transaction_type": self.transaction_type.value}

    @classmethod
    def from_dict(cls: Type[Transaction], value: Dict[str, Any]) -> Transaction:
        """
        Construct a new Transaction from a dictionary of parameters.

        Args:
            value: The value to construct the Transaction from.

        Returns:
            A new Transaction object, constructed using the given parameters.

        Raises:
            XRPLModelException: If the dictionary provided is invalid.
        """
        if cls.__name__ == "Transaction":
            # using `Transaction.from_dict` and not a subclass
            if "transaction_type" not in value:
                raise XRPLModelException(
                    "Transaction does not include transaction_type."
                )
            correct_type = cls.get_transaction_type(value["transaction_type"])
            return correct_type.from_dict(value)
        else:
            if "transaction_type" in value:
                if value["transaction_type"] != cls.__name__:
                    transaction_type = value["transaction_type"]
                    raise XRPLModelException(
                        f"Using wrong constructor: using f{cls.__name__} constructor "
                        f"with transaction type f{transaction_type}."
                    )
                value = {**value}
                del value["transaction_type"]
            return cast(Transaction, super(Transaction, cls).from_dict(value))

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
    def get_transaction_type(
        cls: Type[Transaction], transaction_type: str
    ) -> Type[Transaction]:
        """
        Returns the correct transaction type based on the string name.

        Args:
            transaction_type: The String name of the Transaction object.

        Returns:
            The transaction class with the given name.

        Raises:
            XRPLModelException: If `transaction_type` is not a valid Transaction type.
        """
        import xrpl.models.transactions as transaction_models

        transaction_types: Dict[str, Type[Transaction]] = {
            t.value: getattr(transaction_models, t)
            for t in transaction_models.transaction.TransactionType
        }
        if transaction_type in transaction_types:
            return transaction_types[transaction_type]

        raise XRPLModelException(f"{transaction_type} is not a valid Transaction type")
