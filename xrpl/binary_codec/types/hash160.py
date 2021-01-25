"""A hash field with a width of 160 bits (20 bytes).
`See Hash Fields <https://xrpl.org/serialization.html#hash-fields>`_
"""
from xrpl.binary_codec.binary_wrappers.binary_parser import BinaryParser
from xrpl.binary_codec.types.hash import Hash


class Hash160(Hash):
    """
    A hash field with a width of 160 bits (20 bytes).
    `See Hash Fields <https://xrpl.org/serialization.html#hash-fields>`_


    Attributes:
        width: The length of this hash in bytes.
    """

    width = 20

    def __init__(self, buffer: bytes = None):
        """Construct a Hash160."""
        buffer = buffer if buffer is not None else bytes(20)
        super().__init__(buffer)

    @classmethod
    def from_value(cls, value: str):
        """Construct a Hash object from a hex string."""
        return cls(bytes.fromhex(value))

    @classmethod
    def from_parser(cls, parser: BinaryParser, length_hint: int = None):
        """Construct a Hash object from an existing BinaryParser."""
        num_bytes = length_hint if length_hint is not None else cls.width
        return cls(parser.read(num_bytes))
