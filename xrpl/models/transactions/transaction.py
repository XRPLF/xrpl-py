"""The base model for all transactions and their nested object types."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha512
from typing import Any, Dict, List, Optional, Type, Union, cast

from typing_extensions import Final

from xrpl.core.binarycodec import encode
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.base_model import BaseModel
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.flags import check_false_flag_definition, interface_to_flag_list
from xrpl.models.requests import PathStep
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.types import PseudoTransactionType, TransactionType
from xrpl.models.types import XRPL_VALUE_TYPE
from xrpl.models.utils import require_kwargs_on_init

_TRANSACTION_HASH_PREFIX: Final[int] = 0x54584E00
# This is used to make exceptions when converting dictionary keys to xrpl JSON
# keys. We snake case keys, but some keys are abbreviations.
_ABBREVIATIONS: Final[Dict[str, str]] = {
    "unl": "UNL",
    "id": "ID",
    "uri": "URI",
    "nftoken": "NFToken",
}


def transaction_json_to_binary_codec_form(
    dictionary: Dict[str, XRPL_VALUE_TYPE]
) -> Dict[str, XRPL_VALUE_TYPE]:
    """
    Returns a new dictionary in which the keys have been formatted as CamelCase and
    standardized to be serialized by the binary codec.

    Args:
        dictionary: The dictionary to be reformatted.

    Returns:
        A new dictionary object that has been reformatted.
    """
    # This method should be made private when it is removed from `xrpl.transactions`
    return {
        _key_to_tx_json(key): _value_to_tx_json(value)
        for (key, value) in dictionary.items()
    }


def _key_to_tx_json(key: str) -> str:
    """
    Transforms snake_case to PascalCase. For example:
        1. 'transaction_type' becomes 'TransactionType'
        2. 'URI' becomes 'uri'

    Known abbreviations (example 2 above) need to be enumerated in _ABBREVIATIONS.
    """
    return "".join(
        [
            _ABBREVIATIONS[word] if word in _ABBREVIATIONS else word.capitalize()
            for word in key.split("_")
        ]
    )


def _value_to_tx_json(value: XRPL_VALUE_TYPE) -> XRPL_VALUE_TYPE:
    # IssuedCurrencyAmount and PathStep are special cases and should not be snake cased
    # and only contain primitive members
    if IssuedCurrencyAmount.is_dict_of_model(value) or PathStep.is_dict_of_model(value):
        return value
    if isinstance(value, dict):
        return transaction_json_to_binary_codec_form(value)
    if isinstance(value, list):
        return [_value_to_tx_json(sub_value) for sub_value in value]
    return value


@require_kwargs_on_init
@dataclass(frozen=True)
class Memo(BaseModel):
    """
    An arbitrary piece of data attached to a transaction. A transaction can
    have multiple Memo objects as an array in the Memos field.
    Must contain one or more of ``memo_data``, ``memo_format``, and
    ``memo_type``.
    """

    memo_data: Optional[str] = None
    """The data of the memo, as a hexadecimal string."""

    memo_format: Optional[str] = None
    """
    The format of the memo, as a hexadecimal string. Conventionally, this
    should be the `MIME type
    <http://www.iana.org/assignments/media-types/media-types.xhtml>`_
    of the memo data.
    """

    memo_type: Optional[str] = None
    """
    The type of the memo, as a hexadecimal string. Conventionally, this
    should be an `RFC 5988 relation
    <http://tools.ietf.org/html/rfc5988#section-4>`_ defining the format of
    the memo data.
    """

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

    @classmethod
    def from_dict(cls: Type[Memo], value: Dict[str, Any]) -> Memo:
        """
        Construct a new Memo from a dictionary of parameters.

        Args:
            value: The value to construct the Memo from.

        Returns:
            A new Memo object, constructed using the given parameters.

        Raises:
            XRPLModelException: If the dictionary provided is invalid.
        """
        if "memo" not in value:
            return cast(Memo, super(Memo, cls).from_dict(value))
        return cast(Memo, super(Memo, cls).from_dict(value["memo"]))

    def to_dict(self: Memo) -> Dict[str, Any]:
        """
        Returns the dictionary representation of a Memo.

        Returns:
            The dictionary representation of a Memo.
        """
        return {"memo": super().to_dict()}


@require_kwargs_on_init
@dataclass(frozen=True)
class Signer(BaseModel):
    """
    One Signer in a multi-signature. A multi-signed transaction can have an
    array of up to 8 Signers, each contributing a signature, in the Signers
    field.
    """

    account: str = REQUIRED  # type: ignore
    """
    The address of the Signer. This can be a funded account in the XRP
    Ledger or an unfunded address.
    This field is required.

    :meta hide-value:
    """

    txn_signature: str = REQUIRED  # type: ignore
    """
    The signature that this Signer provided for this transaction.
    This field is required.

    :meta hide-value:
    """

    signing_pub_key: str = REQUIRED  # type: ignore
    """
    The public key that should be used to verify this Signer's signature.
    This field is required.

    :meta hide-value:
    """

    @classmethod
    def is_dict_of_model(cls: Type[Signer], dictionary: Any) -> bool:
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

    @classmethod
    def from_dict(cls: Type[Signer], value: Dict[str, Any]) -> Signer:
        """
        Construct a new Signer from a dictionary of parameters.

        Args:
            value: The value to construct the Signer from.

        Returns:
            A new Signer object, constructed using the given parameters.

        Raises:
            XRPLModelException: If the dictionary provided is invalid.
        """
        if "signer" not in value:
            return cast(Signer, super(Signer, cls).from_dict(value))
        return cast(Signer, super(Signer, cls).from_dict(value["signer"]))

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

    account: str = REQUIRED  # type: ignore
    """
    The address of the sender of the transaction. Required.

    :meta hide-value:
    """

    transaction_type: Union[
        TransactionType, PseudoTransactionType
    ] = REQUIRED  # type: ignore

    fee: Optional[str] = None  # auto-fillable
    """
    (Auto-fillable) The amount of XRP to destroy as a cost to send this
    transaction. See `Transaction Cost
    <https://xrpl.org/transaction-cost.html>`_ for details.
    """

    sequence: Optional[int] = None  # auto-fillable
    """
    (Auto-fillable) The sequence number of the transaction. Must match the
    sending account's next unused sequence number. See `Account Sequence
    <https://xrpl.org/basic-data-types.html#account-sequence>`_ for details.
    """

    account_txn_id: Optional[str] = None
    """
    A hash value identifying a previous transaction from the same sender. If
    provided, this transaction is only considered valid if the identified
    transaction is the most recent transaction sent by this address. See
    `AccountTxnID
    <https://xrpl.org/transaction-common-fields.html#accounttxnid>`_ for
    details.
    """

    flags: Union[Dict[str, bool], int, List[int]] = 0
    """
    A List of flags, or a bitwise map of flags, modifying this transaction's
    behavior. See `Flags Field
    <https://xrpl.org/transaction-common-fields.html#flags-field>`_ for more details.
    """

    last_ledger_sequence: Optional[int] = None
    """
    The highest ledger index this transaction can appear in. Specifying this
    field places a strict upper limit on how long the transaction can wait
    to be validated or rejected. See `Reliable Transaction Submission
    <https://xrpl.org/reliable-transaction-submission.html>`_ for details.
    """

    memos: Optional[List[Memo]] = None
    """Additional arbitrary information attached to this transaction."""

    signers: Optional[List[Signer]] = None
    """
    Signing data authorizing a multi-signed transaction. Added during
    multi-signing.
    """

    source_tag: Optional[int] = None
    """
    An arbitrary `source tag
    <https://xrpl.org/source-and-destination-tags.html>`_ representing a
    hosted user or specific purpose at the sending account where this
    transaction comes from.
    """

    signing_pub_key: str = ""
    """
    The public key authorizing a single-signed transaction. Automatically
    added during signing.
    """

    txn_signature: Optional[str] = None
    """
    The cryptographic signature from the sender that authorizes this
    transaction. Automatically added during signing.
    """

    def to_dict(self: Transaction) -> Dict[str, Any]:
        """
        Returns the dictionary representation of a Transaction.

        Returns:
            The dictionary representation of a Transaction.
        """
        # we need to override this because transaction_type is using ``field``
        # which will not include the value in the objects __dict__
        return {
            **super().to_dict(),
            "transaction_type": self.transaction_type.value,
            "flags": self._flags_to_int(),
        }

    def _iter_to_int(
        self: Transaction,
        lst: List[int],
    ) -> int:
        """Calculate flag as int."""
        accumulator = 0
        for flag in lst:
            accumulator |= flag
        return accumulator

    def _flags_to_int(self: Transaction) -> int:
        if isinstance(self.flags, int):
            return self.flags
        check_false_flag_definition(tx_type=self.transaction_type, tx_flags=self.flags)
        if isinstance(self.flags, dict):
            return self._iter_to_int(
                lst=interface_to_flag_list(
                    tx_type=self.transaction_type,
                    tx_flags=self.flags,
                )
            )

        return self._iter_to_int(lst=self.flags)

    def to_xrpl(self: Transaction) -> Dict[str, Any]:
        """
        Creates a JSON-like dictionary in the JSON format used by the binary codec
        based on the Transaction object.

        Returns:
            A JSON-like dictionary in the JSON format used by the binary codec.
        """
        return transaction_json_to_binary_codec_form(self.to_dict())

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
        if cls.__name__ == "Transaction" or cls.__name__ == "PseudoTransaction":
            # using `(Pseudo)Transaction.from_dict` and not a subclass
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
                        f"Using wrong constructor: using {cls.__name__} constructor "
                        f"with transaction type {transaction_type}."
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
        if isinstance(self.flags, int):
            return self.flags & flag != 0
        elif isinstance(self.flags, dict):
            return flag in interface_to_flag_list(
                tx_type=self.transaction_type,
                tx_flags=self.flags,
            )
        else:  # is List[int]
            return flag in self.flags

    def get_hash(self: Transaction) -> str:
        """
        Hashes the Transaction object as the ledger does. Only valid for signed
        Transaction objects.

        Returns:
            The hash of the Transaction object.

        Raises:
            XRPLModelException: if the Transaction is unsigned.
        """
        if self.txn_signature is None:
            raise XRPLModelException(
                "Cannot get the hash from an unsigned Transaction."
            )
        prefix = hex(_TRANSACTION_HASH_PREFIX)[2:].upper()
        encoded_str = bytes.fromhex(prefix + encode(self.to_xrpl()))
        return sha512(encoded_str).digest().hex().upper()[:64]

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
        import xrpl.models.transactions.pseudo_transactions as pseudo_transaction_models

        transaction_types: Dict[str, Type[Transaction]] = {
            t.value: getattr(transaction_models, t)
            for t in transaction_models.types.TransactionType
        }
        if transaction_type in transaction_types:
            return transaction_types[transaction_type]

        pseudo_transaction_types: Dict[str, Type[Transaction]] = {
            t.value: getattr(pseudo_transaction_models, t)
            for t in transaction_models.types.PseudoTransactionType
        }
        if transaction_type in pseudo_transaction_types:
            return pseudo_transaction_types[transaction_type]

        raise XRPLModelException(f"{transaction_type} is not a valid Transaction type")
