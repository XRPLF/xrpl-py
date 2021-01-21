"""A hash field with a width of 160 bits (20 bytes)."""
from xrpl.binary_codec.types.hash import Hash


class Hash160(Hash):
    """
    A hash field with a width of 160 bits (20 bytes).

    Attributes:
        width: The length of this hash in bytes.
    """

    width = 20

    def __init__(self, buffer: bytes = None):
        """Construct a Hash160."""
        buffer = buffer if buffer is not None else bytes(20)
        super().__init__(buffer)
