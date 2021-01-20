"""TODO"""
from abc import ABC, abstractmethod


class UInt(ABC):
    def __init__(self, uint_bytes):
        self.bytes = uint_bytes

    def __eq__(self, other):
        return self.value == other.value

    def __ne__(self, other):
        return self.value != other.value

    def __lt__(self, other):
        return self.value < other.value

    def __le__(self, other):
        return self.value <= other.value

    def __gt__(self, other):
        return self.value > other.value

    def __ge__(self, other):
        return self.value >= other.value

    def to_json(self):
        if isinstance(self.value, (int, float)):
            return self.value
        else:
            return str(self.value)

    @property
    @abstractmethod
    def value(self):
        raise NotImplementedError("UInt.value not implemented.")
