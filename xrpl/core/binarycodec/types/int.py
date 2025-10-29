"""Base class for serializing and deserializing signed integers.
See `UInt Fields <https://xrpl.org/serialization.html#uint-fields>`_
"""

from __future__ import annotations

from typing_extensions import Final, Self

from xrpl.core.binarycodec.types.uint import UInt

_WIDTH: Final[int] = 4  # 32 / 8


class Int(UInt):
    """Base class for serializing and deserializing unsigned integers.
    See `UInt Fields <https://xrpl.org/serialization.html#uint-fields>`_
    """

    @property
    def value(self: Self) -> int:
        """
        Get the value of the Int represented by `self.buffer`.

        Returns:
            The int value of the Int.
        """
        return int.from_bytes(self.buffer, byteorder="big", signed=True)
