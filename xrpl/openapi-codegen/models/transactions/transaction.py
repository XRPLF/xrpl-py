"""Model for Transaction."""

from dataclasses import dataclass
from hashlib import sha512
from typing import Any, Dict, List, Optional, Type, Union
from typing_extensions import Final, Self
from xrpl.core.binarycodec import decode, encode
from xrpl.models.base_model import ABBREVIATIONS, BaseModel
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.flags import check_false_flag_definition, interface_to_flag_list
from xrpl.models.types import XRPL_VALUE_TYPE
from xrpl.models.utils import REQUIRED
from xrpl.models.memo import Memo
from xrpl.models.path_step import PathStep
from xrpl.models.token_amount import TokenAmount

_TRANSACTION_HASH_PREFIX: Final[int] = 0x54584E00


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
    # TokenAmount and PathStep are special cases and should not be snake cased
    # and only contain primitive members
    if isinstance(value, list) and all(PathStep.is_dict_of_model(v) for v in value):
        return value
    if TokenAmount.is_dict_of_model(value):
        return value
    if isinstance(value, dict):
        return transaction_json_to_binary_codec_form(value)
    if isinstance(value, list):
        return [_value_to_tx_json(sub_value) for sub_value in value]
    return value


from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class Transaction(BaseModel):
    account: str = REQUIRED
    """
    The unique address of the account that initiated the transaction.
    """

    transaction_type: str = REQUIRED
    """
    The type of transaction. Valid transaction types include: Payment, OfferCreate,
    TrustSet, and many others.
    """

    fee: Optional[str] = None
    """
    Integer amount of XRP, in drops, to be destroyed as a cost for distributing this
    transaction to the network. Some transaction types have different minimum requirements.
    See Transaction Cost for details.
    """

    sequence: Optional[int] = None
    """
    The sequence number of the account sending the transaction. A transaction is only valid
    if the Sequence number is exactly 1 greater than the previous transaction from the same
    account. The special case 0 means the transaction is using a Ticket instead.
    """

    account_txn_id: Optional[str] = None
    """
    Hash value identifying another transaction. If provided, this transaction is only valid
    if the sending account's previously-sent transaction matches the provided hash.
    """

    flags: Optional[int] = None
    """
    Set of bit-flags for this transaction.
    """

    last_ledger_sequence: Optional[int] = None
    """
    Highest ledger index this transaction can appear in. Specifying this field places a
    strict upper limit on how long the transaction can wait to be validated or rejected.
    """

    memos: Optional[List[Memo]] = None
    """
    The Memos field includes arbitrary messaging data with the transaction. It is presented
    as an array of objects. Each object has only one field, Memo, which in turn contains
    another object. The Memos field is limited to no more than 1 KB in size (when serialized
    in binary format). The MemoType and MemoFormat fields should only consist of the
    following characters -
    ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~:/?#[]@!$&'()*+,;=%
    """

    network_id: Optional[int] = None
    """
    The network ID of the chain this transaction is intended for. MUST BE OMITTED for
    Mainnet and some test networks. REQUIRED on chains whose network ID is 1025 or higher.
    """

    signers: Optional[List[Dict[str, Any]]] = None
    """
    Array of objects that represent a multi-signature which authorizes this transaction.
    """

    source_tag: Optional[int] = None
    """
    Arbitrary integer used to identify the reason for this payment, or a sender on whose
    behalf this transaction is made.
    """

    signing_pub_key: Optional[str] = None
    """
    Hex representation of the public key that corresponds to the private key used to sign
    this transaction. If an empty string, indicates a multi-signature is present in the
    Signers field instead.
    """

    ticket_sequence: Optional[int] = None
    """
    The sequence number of the ticket to use in place of a Sequence number. If this is
    provided, Sequence must be 0. Cannot be used with AccountTxnID.
    """

    txn_signature: Optional[str] = None
    """
    The signature that verifies this transaction as originating from the account it says it
    is from.
    """

    def _get_errors(self: Self) -> Dict[str, str]:
        # import must be here to avoid circular dependencies
        from xrpl.wallet.main import Wallet

        errors = super()._get_errors()
        if self.ticket_sequence is not None and (
            (self.sequence is not None and self.sequence != 0)
            or self.account_txn_id is not None
        ):
            errors[
                "Transaction"
            ] = """If ticket_sequence is provided,
            account_txn_id must be None and sequence must be None or 0"""

        if isinstance(self.account, Wallet):
            errors["account"] = "Must pass in `wallet.address`, not `wallet`."

        return errors

    def to_dict(self: Self) -> Dict[str, Any]:
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
        self: Self,
        lst: List[int],
    ) -> int:
        """Calculate flag as int."""
        accumulator = 0
        for flag in lst:
            accumulator |= flag
        return accumulator

    def _flags_to_int(self: Self) -> int:
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
            return correct_type.from_dict(value)  # type: ignore
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
            return super(Transaction, cls).from_dict(value)

    def has_flag(self: Self, flag: int) -> bool:
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
        if self.txn_signature is None and self.signers is None:
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

    def _get_errors(self: Transaction) -> Dict[str, str]:
        errors = super._get_errors()
        return errors
