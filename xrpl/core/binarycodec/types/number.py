import struct
from typing import Optional, Type

from typing_extensions import Self

from xrpl.core.binarycodec.binary_wrappers.binary_parser import BinaryParser
from xrpl.core.binarycodec.exceptions import XRPLBinaryCodecException
from xrpl.core.binarycodec.types.serialized_type import SerializedType


class Number(SerializedType):
    """Codec for serializing and deserializing Number fields."""

    def __init__(self: Self, buffer: bytes) -> None:
        """Construct a Number from given bytes."""
        super().__init__(buffer)

    @classmethod
    def from_parser(  # noqa: D102
        cls: Type[Self],
        parser: BinaryParser,
        length_hint: Optional[int] = None,  # noqa: ANN401
    ) -> Self:
        # Number type consists of two cpp std::uint_64t (mantissa) and
        # std::uint_32t (exponent) types which are 8 bytes and 4 bytes respectively
        return cls(parser.read(12))

    @classmethod
    def from_value(cls: Type[Self], value: str) -> Self:
        return cls(struct.pack(">d", float(value)))

    def to_json(self: Self) -> str:
        unpack_elems = struct.unpack(">d", self.buffer)
        if len(unpack_elems) != 1:
            raise XRPLBinaryCodecException(
                "Deserialization of Number type did not produce exactly one element"
            )
        return str(unpack_elems[0])
