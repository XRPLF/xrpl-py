"""The base model for all transactions and their nested object types."""
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
    An arbitrary piece of data attached to a transaction. A transaction can
    have multiple Memo objects as an array in the Memos field.
    Must contain one or more of ``memo_data``, ``memo_format``, and
    ``memo_type``.
    """

    #: The data of the memo, as a hexadecimal string.
    memo_data: Optional[str] = None

    #: The format of the memo, as a hexadecimal string. Conventionally, this
    #: should be the `MIME type
    #: <http://www.iana.org/assignments/media-types/media-types.xhtml>`_
    #: of the memo data.
    memo_format: Optional[str] = None

    #: The type of the memo, as a hexadecimal string. Conventionally, this
    #: should be an `RFC 5988 relation
    #: <http://tools.ietf.org/html/rfc5988#section-4>`_ defining the format of
    #: the memo data.
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
    One Signer in a multi-signature. A multi-signed transaction can have an
    array of up to 8 Signers, each contributing a signature, in the Signers
    field.
    """

    #: The address of the Signer. This can be a funded account in the XRP
    #: Ledger or an unfunded address.
    #: This field is required.
    account: str = REQUIRED  # type: ignore

    #: The signature that this Signer provided for this transaction.
    #: This field is required.
    txn_signature: str = REQUIRED  # type: ignore

    #: The public key that should be used to verify this Signer's signature.
    #: This field is required.
    signing_pub_key: str = REQUIRED  # type: ignore

    @classmethod
    def is_dict_of_model(cls: Type[Signer], dictionary: Dict[str, Any]) -> bool:
        """
        Returns True if the input dictionary was derived by the `to_dict`
        method of an instance of this class. In other words, True if this is
        a dictionary representation of an instance of this class.

        NOTE: does not account for model inheritance, IE will only return True
        if dictionary represents an instance of this class, but not if
        dictionary represents an instance of a subclass of this class.

        Args:
            dictionary: The dictionary to check.

        Returns:
            True if dictionary is a dict representation of an instance of this
            class.
        """
        return (
            isinstance(dictionary, dict)
            and "signer" in dictionary
            and super().is_dict_of_model(dictionary["signer"])
        )

    def to_dict(self: Signer) -> Dict[str, Any]:
        """
        Returns the dictionary representation of a Signer.

        Returns:
            The dictionary representation of a Signer.
        """
        return {"signer": super().to_dict()}


@require_kwargs_on_init
@dataclass(frozen=True)
class Transaction(BaseModel):
    """
    The base class for all `transaction types
    <https://xrpl.org/transaction-types.html>`_. Represents `fields common to all
    transaction types <https://xrpl.org/transaction-common-fields.html>`_.
    """

    # TODO: figure out how to get documentation to ignore the default value
    # in theory this should be doable with `#: :meta hide-value:` but it's not quite
    # working

    #: The address of the sender of the transaction.
    #: This field is required.
    account: str = REQUIRED  # type: ignore

    transaction_type: TransactionType = REQUIRED  # type: ignore

    #: (Auto-fillable) The amount of XRP to destroy as a cost to send this
    #: transaction. See `Transaction Cost
    #: <https://xrpl.org/transaction-cost.html>`_ for details.
    fee: Optional[str] = None  # auto-fillable

    #: (Auto-fillable) The sequence number of the transaction. Must match the
    #: sending account's next unused sequence number. See `Account Sequence
    #: <https://xrpl.org/basic-data-types.html#account-sequence>`_ for details.
    sequence: Optional[int] = None  # auto-fillable

    #: A hash value identifying a previous transaction from the same sender. If
    #: provided, this transaction is only considered valid if the identified
    #: transaction is the most recent transaction sent by this address. See
    #: `AccountTxnID
    #: <https://xrpl.org/transaction-common-fields.html#accounttxnid>`_ for
    #: details.
    account_txn_id: Optional[str] = None

    #: A bitwise map of flags modifying this transaction's behavior. See `Flags
    #: Field <https://xrpl.org/transaction-common-fields.html#flags-field>`_ for
    #: more details.
    flags: int = 0

    #: The highest ledger index this transaction can appear in. Specifying this
    #: field places a strict upper limit on how long the transaction can wait
    #: to be validated or rejected. See `Reliable Transaction Submission
    #: <https://xrpl.org/reliable-transaction-submission.html>`_ for details.
    last_ledger_sequence: Optional[int] = None

    #: Additional arbitrary information attached to this transaction.
    memos: Optional[List[Memo]] = None

    #: Signing data authorizing a multi-signed transaction. Added during
    #: multi-signing.
    signers: Optional[List[Signer]] = None

    #: An arbitrary `source tag
    #: <https://xrpl.org/source-and-destination-tags.html>`_ representing a
    #: hosted user or specific purpose at the sending account where this
    #: transaction comes from.
    source_tag: Optional[int] = None

    #: The public key authorizing a single-signed transaction. Automatically
    #: added during signing.
    signing_pub_key: str = ""

    #: The cryptographic signature from the sender that authorizes this
    #: transaction. Automatically added during signing.
    txn_signature: Optional[str] = None

    def to_dict(self: Transaction) -> Dict[str, Any]:
        """
        Returns the dictionary representation of a Transaction.

        Returns:
            The dictionary representation of a Transaction.
        """
        # we need to override this because transaction_type is using ``field``
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
