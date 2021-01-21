"""Base class for XRPL Hash types."""
from xrpl.binary_codec.types.serialized_type import SerializedType
from xrpl.binary_codec.binary_wrappers.binary_parser import BinaryParser
from xrpl.binary_codec.exceptions import XRPLBinaryCodecException


class Hash(SerializedType):
    """Base class for XRPL Hash types."""

    def __init__(self, buffer: bytes, width: int):
        """
        Construct a Hash.

        :param buffer: The byte buffer that will be used to store
                        the serialized version of this field.
        :param width: The length of the hash in bytes.
        """
        super().__init__(buffer)
        if len(buffer) != width:
            raise XRPLBinaryCodecException("Invalid hash length {}".format(len(buffer)))
        self.width = width

    def __str__(self):
        """Returns a hex-encoded string representation of the bytes buffer."""
        return self.to_hex()

    # TODO: what is the right way to do this??
    def from_value(self, value):
        """Construct a Hash object from a hex string."""
        return super().from_parser(BinaryParser(value), self.width)

    # TODO: same here??  what does this look like in python?
    def from_parser(self, parser, length_hint: int = None):
        """Construct a Hash object from an existing BinaryParser."""
        return self.__init__(parser.read())
