"""DOCSTRING"""
from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class Wrapper(ABC, Generic[T]):
    """A typed wrapper for single values."""

    value: T

    # Should validation go in __pre_init__?
    def to_string(self: Wrapper) -> str:
        """
        Converts the value to a string.

        Returns:
            A string representation of the underlying value.
        """
        return str(self.value)
