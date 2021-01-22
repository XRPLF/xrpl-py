"""Base class for serializing and deserializing unsigned integers."""
from abc import ABC, abstractmethod


class UInt(ABC):
    """Base class for serializing and deserializing unsigned integers."""

    def __init__(self, buffer):
        """Construct a new UInt type from a `bytes` value."""
        self.buffer = buffer

    def __eq__(self, other):
        """Determine whether two UInt objects are equal."""
        if isinstance(other, int):
            return self.value == other
        return self.value == other.value

    def __ne__(self, other):
        """Determine whether two UInt objects are unequal."""
        if isinstance(other, int):
            return self.value != other
        return self.value != other.value

    def __lt__(self, other):
        """Determine whether one UInt object is less than another."""
        if isinstance(other, int):
            return self.value < other
        return self.value < other.value

    def __le__(self, other):
        """Determine whether one UInt object is less than or equal to another."""
        if isinstance(other, int):
            return self.value <= other
        return self.value <= other.value

    def __gt__(self, other):
        """Determine whether one UInt object is greater than another."""
        if isinstance(other, int):
            return self.value > other
        return self.value > other.value

    def __ge__(self, other):
        """Determine whether one UInt object is greater than or equal to another."""
        if isinstance(other, int):
            return self.value >= other
        return self.value >= other.value

    def to_json(self):
        """Convert a UInt object to JSON."""
        if isinstance(self.value, int):
            return self.value
        return str(self.value)

    @property
    @abstractmethod
    def value(self):
        """Get the value of the UInt represented by `self.buffer`."""
        raise NotImplementedError("UInt.value not implemented.")
