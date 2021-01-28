"""The base class for all binary codec types."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional, Union


class SerializedType(ABC):
    """The base class for all binary codec types."""

    def __init__(self: SerializedType, buffer: bytes = bytes()) -> None:
        """Construct a new SerializedType."""
        self.buffer = buffer

    @abstractmethod
    def from_parser(
        self: SerializedType,
        parser: Any,
        length_hint: Optional[int] = None
        # TODO: resolve Any (can't be `BinaryParser` because of circular imports)
    ) -> SerializedType:
        """Construct a new SerializedType from a BinaryParser."""
        raise NotImplementedError("SerializedType.from_parser not implemented.")

    @abstractmethod
    def from_value(
        self: SerializedType, value: Union[SerializedType, str]
    ) -> SerializedType:
        """Construct a new SerializedType from a literal value."""
        raise NotImplementedError("SerializedType.from_value not implemented.")

    def to_byte_sink(self: SerializedType, bytesink: bytearray) -> None:
        """
        Write the bytes representation of a SerializedType to a bytearray.
        :param bytesink: The bytearray to write self.buffer to.
        """
        bytesink.extend(self.buffer)

    def to_bytes(self: SerializedType) -> bytes:
        """Get the bytes representation of a SerializedType."""
        return self.buffer

    def to_json(self: SerializedType) -> str:
        """
        Return the JSON representation of a SerializedType.
        If not overridden, returns hex string representation of bytes.
        """
        return self.to_hex()

    def to_string(self: SerializedType) -> str:
        """Returns the hex string representation of self.buffer."""
        return self.to_hex()

    def to_hex(self: SerializedType) -> str:
        """Get the hex representation of a SerializedType's bytes."""
        return self.buffer.hex()
