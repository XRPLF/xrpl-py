"""The base class for all binary codec types."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Union

from xrpl.binary_codec.binary_wrappers.binary_parser import BinaryParser


class SerializedType(ABC):
    """The base class for all binary codec types."""

    def __init__(self, buffer: bytes) -> None:
        """Construct a new SerializedType."""
        if buffer is not None:
            self.buffer = buffer
        else:
            self.buffer = bytes()

    @abstractmethod
    def from_parser(
        self, parser: BinaryParser, length_hint: Optional[int] = None
    ) -> SerializedType:
        """Construct a new SerializedType from a BinaryParser."""
        raise NotImplementedError("SerializedType.from_parser not implemented.")

    @abstractmethod
    def from_value(self, value: Union[SerializedType, str]) -> SerializedType:
        """Construct a new SerializedType from a literal value."""
        raise NotImplementedError("SerializedType.from_value not implemented.")

    def to_byte_sink(self, bytesink: bytearray) -> None:
        """
        Write the bytes representation of a SerializedType to a bytearray.
        :param bytesink: The bytearray to write self.buffer to.
        """
        bytesink.append(self.buffer)

    def to_bytes(self) -> bytes:
        """Get the bytes representation of a SerializedType."""
        return self.buffer

    def to_json(self) -> str:
        """
        Return the JSON representation of a SerializedType.
        If not overridden, returns hex string representation of bytes.
        """
        return self.to_hex()

    def to_string(self) -> str:
        """Returns the hex string representation of self.buffer."""
        return self.to_hex()

    def to_hex(self) -> str:
        """Get the hex representation of a SerializedType's bytes."""
        return self.buffer.hex()
