"""Base class for XRPL Hash types."""
from abc import ABC
from xrpl.binary_codec.types.serialized_type import SerializedType
from xrpl.binary_codec.binary_wrappers.binary_parser import BinaryParser
from xrpl.binary_codec.exceptions import XRPLBinaryCodecException


class Hash(SerializedType, ABC):
    """
    Base class for XRPL Hash types.

    Attributes:
        width:  The length of this hash in bytes.
    """

    width: int

    def __init__(self, buffer: bytes):
        """
        Construct a Hash.

        :param buffer: The byte buffer that will be used to store
                        the serialized encoding of this field.
        """
        if len(buffer) != self.width:
            raise XRPLBinaryCodecException("Invalid hash length {}".format(len(buffer)))
        super().__init__(buffer)

    def __str__(self):
        """Returns a hex-encoded string representation of the bytes buffer."""
        return self.to_hex()

    @classmethod
    def from_value(cls, value: str):
        """Construct a Hash object from a hex string."""
        return cls.from_parser(BinaryParser(value), cls.width)

    @classmethod
    def from_parser(cls, parser, length_hint: int = None):
        """Construct a Hash object from an existing BinaryParser."""
        num_bytes = length_hint if length_hint is not None else cls.width
        return cls.__init__(parser.read(num_bytes))
