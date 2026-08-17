"""The base model for all transactions and their nested object types."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha512
from typing import Any, Dict, List, Optional, Type, Union, cast

from typing_extensions import Final, Self

from xrpl.core.binarycodec import decode, encode
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.amounts.mpt_amount import MPTAmount
from xrpl.models.base_model import ABBREVIATIONS, BaseModel
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.flags import (
    FlagInterface,
    check_false_flag_definition,
    interface_to_flag_list,
)
from xrpl.models.nested_model import NestedModel
from xrpl.models.requests import PathStep
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.types import PseudoTransactionType, TransactionType
from xrpl.models.types import XRPL_VALUE_TYPE

_TRANSACTION_HASH_PREFIX: Final[int] = 0x54584E00

_SPF_SPONSOR_FEE: Final[int] = 0x00000001
_SPF_SPONSOR_RESERVE: Final[int] = 0x00000002
_SPF_SPONSOR_FLAG_MASK: Final[int] = ~(_SPF_SPONSOR_FEE | _SPF_SPONSOR_RESERVE)


def transaction_json_to_binary_codec_form(
    dictionary: Dict[str, XRPL_VALUE_TYPE],
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

    Known abbreviations (example 2 above) need to be enumerated in ABBREVIATIONS.
    """
    return "".join(
        [
            ABBREVIATIONS[word] if word in ABBREVIATIONS else word.capitalize()
            for word in key.split("_")
        ]
    )


def _value_to_tx_json(value: XRPL_VALUE_TYPE) -> XRPL_VALUE_TYPE:
    # IssuedCurrencyAmount and PathStep are special cases and should not be snake cased
    # and only contain primitive members
    if isinstance(value, list) and all(PathStep.is_dict_of_model(v) for v in value):
        return value
    if IssuedCurrencyAmount.is_dict_of_model(value):
        return value
    if MPTAmount.is_dict_of_model(value):
        return value
    if isinstance(value, dict):
        return transaction_json_to_binary_codec_form(value)
    if isinstance(value, list):
        return [_value_to_tx_json(sub_value) for sub_value in value]
    return value


@dataclass(frozen=True, kw_only=True)
class Memo(NestedModel):
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

    def _get_errors(self: Self) -> Dict[str, str]:
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


@dataclass(frozen=True, kw_only=True)
class Signer(NestedModel):
    """
    One Signer in a multi-signature. A multi-signed transaction can have an
    array of up to 8 Signers, each contributing a signature, in the Signers
    field.
    """

    account: str = REQUIRED
    """
    The address of the Signer. This can be a funded account in the XRP
    Ledger or an unfunded address.
    This field is required.

    :meta hide-value:
    """

    txn_signature: str = REQUIRED
    """
    The signature that this Signer provided for this transaction.
    This field is required.

    :meta hide-value:
    """

    signing_pub_key: str = REQUIRED
    """
    The public key that should be used to verify this Signer's signature.
    This field is required.

    :meta hide-value:
    """


@dataclass(frozen=True, kw_only=True)
class SponsorSignature(BaseModel):
    """
    The sponsor's signing information for a fee-/reserve-sponsored transaction.

    Fields:
    - signing_pub_key: hex-encoded public key of the sponsor (required if
    txn_signature is set).
    - txn_signature: hex-encoded signature over the canonical transaction
    (required if signing_pub_key is set).
    - signers: optional multisign array reusing the standard Signer objects.

    All three fields are optional, and an **empty** ``SponsorSignature()`` is a
    valid, meaningful value in two cases:

    - **Batch inner transactions**. An inner transaction that
      names a ``sponsor`` must carry an empty placeholder; its *presence* --
      not its contents -- is what tells the ledger that the named sponsor needs
      an entry in the outer transaction's ``BatchSigners``. Populating any of
      the three fields on an inner transaction is rejected.
    - **``simulate``**. The server autofills the sponsor's
      signing fields only when the field is present, so a dry run of a
      sponsored transaction supplies the empty object.

    For an ordinary submitted transaction, populate either
    ``signing_pub_key`` + ``txn_signature`` (single-sign) or ``signers``
    (multi-sign) -- see :func:`xrpl.transaction.sign_as_sponsor`.
    """

    signing_pub_key: Optional[str] = None
    txn_signature: Optional[str] = None
    signers: Optional[List[Signer]] = None

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()

        has_single_sig = (
            self.signing_pub_key is not None or self.txn_signature is not None
        )
        has_multi_sig = self.signers is not None

        if self.signers is not None and len(self.signers) == 0:
            errors["signers"] = (
                "`signers` must not be empty; omit it for the empty placeholder, "
                "or provide at least one signer."
            )
        elif has_single_sig and has_multi_sig:
            errors["SponsorSignature"] = (
                "Cannot set both single-signature fields "
                "(`signing_pub_key`/`txn_signature`) and `signers`."
            )
        elif has_single_sig:
            if self.signing_pub_key is None:
                errors["signing_pub_key"] = (
                    "`signing_pub_key` is required when `txn_signature` is set."
                )
            if self.txn_signature is None:
                errors["txn_signature"] = (
                    "`txn_signature` is required when `signing_pub_key` is set."
                )

        return errors


class TransactionFlag(int, Enum):
    """
    Transactions of the Transaction type support additional values in the Flags field.
    This enum represents those options.
    """

    TF_INNER_BATCH_TXN = 0x40000000


class TransactionFlagInterface(FlagInterface):
    """
    Transactions support additional values in the Flags field. This TypedDict
    represents those options.
    """

    TF_INNER_BATCH_TXN: bool


class SponsorFlag(int, Enum):
    """
    Values for the ``sponsor_flags`` common field, which declares what a sponsor
    is covering. At least one must be set whenever ``sponsor`` is present, and
    the two may be combined.

    These use the ``spf`` prefix rather than ``tf``: they are their own field,
    not part of ``Flags``.
    """

    SPF_SPONSOR_FEE = 0x00000001
    """The sponsor pays the transaction fee."""

    SPF_SPONSOR_RESERVE = 0x00000002
    """The sponsor covers the reserve of any object the transaction creates."""


@dataclass(frozen=True, kw_only=True)
class Transaction(BaseModel):
    """
    The base class for all `transaction types
    <https://xrpl.org/transaction-types.html>`_. Represents `fields common to all
    transaction types <https://xrpl.org/transaction-common-fields.html>`_.
    """

    account: str = REQUIRED
    """
    The address of the sender of the transaction. Required.

    :meta hide-value:
    """

    transaction_type: Union[TransactionType, PseudoTransactionType] = REQUIRED

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

    flags: Optional[Union[Dict[str, bool], int, List[int]]] = None
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

    ticket_sequence: Optional[int] = None
    """
    The sequence number of the ticket to use in place of a Sequence number. If
    this is provided, sequence must be 0. Cannot be used with account_txn_id.
    """

    txn_signature: Optional[str] = None
    """
    The cryptographic signature from the sender that authorizes this
    transaction. Automatically added during signing.
    """

    network_id: Optional[int] = None
    """The network id of the transaction."""

    delegate: Optional[str] = None
    """The delegate account that is sending the transaction."""

    sponsor: Optional[str] = None
    """The sponsoring account covering fees or reserves for this transaction."""

    sponsor_flags: Optional[int] = None
    """What the sponsor is covering. Use :class:`SponsorFlag`
    (``SPF_SPONSOR_FEE`` = 0x1, ``SPF_SPONSOR_RESERVE`` = 0x2); the two may be
    combined. Required whenever ``sponsor`` is set, and must be non-zero."""

    sponsor_signature: Optional[SponsorSignature] = None
    """The sponsor's signing information for co-signed sponsorship."""

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()
        if self.ticket_sequence is not None and (
            (self.sequence is not None and self.sequence != 0)
            or self.account_txn_id is not None
        ):
            errors["Transaction"] = """If ticket_sequence is provided,
            account_txn_id must be None and sequence must be None or 0"""

        if self.account == self.delegate:
            errors["delegate"] = "Account and delegate addresses cannot be the same"

        # ── Sponsor cross-field checks ─────────────────────────────────────────
        if self.sponsor is not None and self.sponsor == self.account:
            errors["sponsor"] = "`sponsor` must differ from `account`."

        # `sponsor` and `sponsor_flags` are all-or-nothing, and the flags must
        # name at least one thing to sponsor. rippled rejects any other
        # combination with temINVALID_FLAG.
        if self.sponsor_flags is not None and not isinstance(self.sponsor_flags, int):
            errors["sponsor_flags"] = "`sponsor_flags` must be an integer."
        elif self.sponsor_flags is not None and self.sponsor is None:
            errors["sponsor_flags"] = "`sponsor_flags` requires `sponsor` to be set."
        elif self.sponsor is not None and self.sponsor_flags is None:
            errors["sponsor_flags"] = (
                "`sponsor_flags` is required when `sponsor` is set. Use "
                "`SponsorFlag.SPF_SPONSOR_FEE` and/or "
                "`SponsorFlag.SPF_SPONSOR_RESERVE`."
            )
        elif self.sponsor_flags is not None and self.sponsor_flags == 0:
            errors["sponsor_flags"] = (
                "`sponsor_flags` must not be zero; at least one of "
                "`SPF_SPONSOR_FEE` (0x1) or `SPF_SPONSOR_RESERVE` (0x2) "
                "must be set."
            )
        elif (
            self.sponsor_flags is not None
            and (self.sponsor_flags & _SPF_SPONSOR_FLAG_MASK) != 0
        ):
            errors["sponsor_flags"] = (
                "`sponsor_flags` may only use bits 0x1 (spfSponsorFee) "
                "and 0x2 (spfSponsorReserve)."
            )

        # Reserve sponsorship and permissioned delegation cannot be combined:
        # the created object's owner would be ambiguous (rippled: temINVALID).
        if (
            self.delegate is not None
            and isinstance(self.sponsor_flags, int)
            and self.sponsor_flags & _SPF_SPONSOR_RESERVE
        ):
            errors["delegate_sponsor"] = (
                "`delegate` cannot be combined with `spfSponsorReserve` (0x2)."
            )

        if self.sponsor_signature is not None and self.sponsor is None:
            errors["sponsor_signature"] = (
                "`sponsor_signature` requires `sponsor` to be set."
            )

        # Pseudo-transactions cannot be sponsored at all: their
        # fees and reserves are covered by the network, not by any one account.
        if self.sponsor is not None and isinstance(
            self.transaction_type, PseudoTransactionType
        ):
            # Distinct key from the `sponsor == account` check above so both
            # errors can surface instead of one overwriting the other.
            errors["sponsor_pseudo_transaction"] = (
                "Pseudo-transactions cannot be sponsored."
            )

        # An outer Batch creates no objects of its own, so reserve sponsorship on
        # it is meaningless and disallowed. Fee sponsorship
        # of the outer Batch is allowed and follows the standard rules; inner
        # transactions should carry spfSponsorReserve instead.
        if (
            self.transaction_type == TransactionType.BATCH
            and isinstance(self.sponsor_flags, int)
            and self.sponsor_flags & _SPF_SPONSOR_RESERVE
        ):
            errors["sponsor_flags"] = (
                "`spfSponsorReserve` (0x2) is not allowed on an outer Batch "
                "transaction. Set it on the inner transactions instead."
            )

        return errors

    def to_dict(self: Self) -> Dict[str, Any]:
        """
        Returns the dictionary representation of a Transaction.

        Returns:
            The dictionary representation of a Transaction.
        """
        # we need to override this because transaction_type is using ``field``
        # which will not include the value in the objects __dict__
        prepared_dict = {
            **super().to_dict(),
            "transaction_type": self.transaction_type.value,
        }
        flags = self._flags_to_int()
        if flags is not None:
            prepared_dict["flags"] = flags
        return prepared_dict

    def _iter_to_int(
        self: Self,
        lst: List[int],
    ) -> int:
        """Calculate flag as int."""
        accumulator = 0
        for flag in lst:
            accumulator |= flag
        return accumulator

    def _flags_to_int(self: Self) -> int | None:
        if self.flags is None:
            return None
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

    def to_xrpl(self: Self) -> Dict[str, Any]:
        """
        Creates a JSON-like dictionary in the JSON format used by the binary codec
        based on the Transaction object.

        Returns:
            A JSON-like dictionary in the JSON format used by the binary codec.
        """
        return transaction_json_to_binary_codec_form(self.to_dict())

    def blob(self: Self) -> str:
        """
        Creates the canonical binary format of the Transaction object.

        Returns:
            The binary-encoded object, as a hexadecimal string.
        """
        return encode(self.to_xrpl())

    @classmethod
    def from_dict(cls: Type[Self], value: Dict[str, Any]) -> Self:
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
            return cast(Self, correct_type.from_dict(value))
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
            return super().from_dict(value)

    def has_flag(self: Self, flag: int) -> bool:
        """
        Returns whether the transaction has the given flag value set.

        Args:
            flag: The given flag value for which the function will determine whether it
                is set.

        Returns:
            Whether the transaction has the given flag value set.

        Raises:
            XRPLModelException: if `self.flags` is invalid.
        """
        if self.flags is None:
            return False
        if isinstance(self.flags, int):
            return self.flags & flag != 0
        elif isinstance(self.flags, dict):
            return flag in interface_to_flag_list(
                tx_type=self.transaction_type,
                tx_flags=self.flags,
            )
        elif isinstance(self.flags, list):
            return flag in self.flags
        else:
            raise XRPLModelException("self.flags is not an int, dict, or list")

    def is_signed(self: Self) -> bool:
        """
        Checks if a transaction has been signed.

        Returns:
            Whether the transaction has been signed
        """
        if self.signers:
            for signer in self.signers:
                if (
                    signer.signing_pub_key is None or len(signer.signing_pub_key) <= 0
                ) or (signer.txn_signature is None or len(signer.txn_signature) <= 0):
                    return False
            return True
        return (
            self.signing_pub_key is not None and len(self.signing_pub_key) > 0
        ) and (self.txn_signature is not None and len(self.txn_signature) > 0)

    def get_hash(self: Self) -> str:
        """
        Hashes the Transaction object as the ledger does. Only valid for signed
        Transaction objects.

        Returns:
            The hash of the Transaction object.

        Raises:
            XRPLModelException: if the Transaction is unsigned.
        """
        if (
            self.txn_signature is None
            and self.signers is None
            and not self.has_flag(TransactionFlag.TF_INNER_BATCH_TXN)
        ):
            raise XRPLModelException(
                "Cannot get the hash from an unsigned Transaction."
            )
        prefix = hex(_TRANSACTION_HASH_PREFIX)[2:].upper()
        encoded_str = bytes.fromhex(prefix + encode(self.to_xrpl()))
        return sha512(encoded_str).digest().hex().upper()[:64]

    @classmethod
    def get_transaction_type(
        cls: Type[Self], transaction_type: str
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

    @staticmethod
    def from_blob(tx_blob: str) -> Transaction:
        """
        Decodes a transaction blob.

        Args:
            tx_blob: the tx blob to decode.

        Returns:
            The formatted transaction.
        """
        return Transaction.from_xrpl(decode(tx_blob))

    @classmethod
    def from_xrpl(cls: Type[Self], value: Union[str, Dict[str, Any]]) -> Self:
        """
        Creates a Transaction object based on a JSON or JSON-string representation of
        data

        In Payment transactions, the DeliverMax field is renamed to the Amount field.

        Args:
            value: The dictionary or JSON string to be instantiated.

        Returns:
            A Transaction object instantiated from the input.

        Raises:
            XRPLModelException: If Payment transactions have different values for
                                amount and deliver_max fields
        """
        processed_value = cls._process_xrpl_json(value)
        # handle the deliver_max alias in Payment transactions
        if (
            "transaction_type" in processed_value
            and processed_value["transaction_type"] == "Payment"
        ) and "deliver_max" in processed_value:
            if (
                "amount" in processed_value
                and processed_value["amount"] != processed_value["deliver_max"]
            ):
                raise XRPLModelException(
                    "Error: amount and deliver_max fields must be equal if both are "
                    + "provided"
                )
            else:
                processed_value["amount"] = processed_value["deliver_max"]

            # deliver_max field is not recognised in the Payment Request format,
            # nor is it supported in the serialization operations.
            del processed_value["deliver_max"]

        return cls.from_dict(processed_value)
