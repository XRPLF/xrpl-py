"""The base class for all binary codec types."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional, Type, Union


class SerializedType(ABC):
    """The base class for all binary codec types."""

    def __init__(self: SerializedType, buffer: bytes = bytes()) -> None:
        """Construct a new SerializedType."""
        self.buffer = buffer

    @classmethod
    def get_type_by_name(cls: SerializedType, name: str) -> Type[SerializedType]:
        """
        Convert the string name of a class to the class object itself.

        Args:
            name: the name of the class.

        Returns:
            The corresponding class object.
        """
        # TODO: figure out if there's a better way to do this
        from xrpl.binary_codec.types.account_id import AccountID
        from xrpl.binary_codec.types.amount import Amount
        from xrpl.binary_codec.types.blob import Blob
        from xrpl.binary_codec.types.currency import Currency
        from xrpl.binary_codec.types.hash128 import Hash128
        from xrpl.binary_codec.types.hash160 import Hash160
        from xrpl.binary_codec.types.hash256 import Hash256
        from xrpl.binary_codec.types.serialized_transaction import SerializedTransaction
        from xrpl.binary_codec.types.serialized_transaction_list import (
            SerializedTransactionList,
        )
        from xrpl.binary_codec.types.uint8 import UInt8
        from xrpl.binary_codec.types.uint16 import UInt16
        from xrpl.binary_codec.types.uint32 import UInt32
        from xrpl.binary_codec.types.uint64 import UInt64

        type_map = {
            "AccountID": AccountID,
            "Amount": Amount,
            "Blob": Blob,
            "Currency": Currency,
            "Hash128": Hash128,
            "Hash160": Hash160,
            "Hash256": Hash256,
            # "PathSet": PathSet, # TODO: uncomment when implemented
            "SerializedTransactionList": SerializedTransactionList,
            "SerializedTransaction": SerializedTransaction,
            "UInt8": UInt8,
            "UInt16": UInt16,
            "UInt32": UInt32,
            "UInt64": UInt64,
            # "Vector256": Vector256, # TODO: uncomment when implemented
        }

        return type_map[name]

    @abstractmethod
    def from_parser(
        self: SerializedType,
        parser: Any,
        length_hint: Optional[int] = None
        # TODO: resolve Any (can't be `BinaryParser` because of circular imports)
    ) -> SerializedType:
        """
        Constructs a new SerializedType from a BinaryParser.

        Args:
            parser: The parser to construct a SerializedType from.
            length_hint: The number of bytes to consume from the parser.

        Raises:
            NotImplementedError: Always.
        """
        raise NotImplementedError("SerializedType.from_parser not implemented.")

    @abstractmethod
    def from_value(
        self: SerializedType, value: Union[SerializedType, str]
    ) -> SerializedType:
        """
        Construct a new SerializedType from a literal value.

        Args:
            value: The value to construct the SerializedType from.

        Raises:
            NotImplementedError: Always.
        """
        raise NotImplementedError("SerializedType.from_value not implemented.")

    def to_byte_sink(self: SerializedType, bytesink: bytearray) -> None:
        """
        Write the bytes representation of a SerializedType to a bytearray.

        Args:
            bytesink: The bytearray to write self.buffer to.

        Returns: None
        """
        bytesink.extend(self.buffer)

    def to_bytes(self: SerializedType) -> bytes:
        """
        Get the bytes representation of a SerializedType.

        Returns:
            The bytes representation of the SerializedType.
        """
        return self.buffer

    def to_json(self: SerializedType) -> str:
        """
        Returns the JSON representation of a SerializedType.

        If not overridden, returns hex string representation of bytes.

        Returns:
            The JSON representation of the SerializedType.
        """
        return self.to_hex()

    def to_string(self: SerializedType) -> str:
        """
        Returns the hex string representation of self.buffer.

        Returns:
            The hex string representation of self.buffer.
        """
        return self.to_hex()

    def to_hex(self: SerializedType) -> str:
        """
        Get the hex representation of a SerializedType's bytes.

        Returns:
            The hex string representation of the SerializedType's bytes.
        """
        return self.buffer.hex()

    def __len__(self: SerializedType) -> int:
        """Get the length of a SerializedType's bytes."""
        return len(self.buffer)
