"""A typed wrapper for single values."""
from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class Wrapper(ABC, Generic[T]):
    """A typed wrapper for single values."""

    value: T

    def __post_init__(self: Wrapper[T]) -> None:
        """Validation after init."""
        self.validate()

    def to_string(self: Wrapper[T]) -> str:
        """
        Converts the value to a string.

        Returns:
            A string representation of the underlying value.
        """
        return str(self.value)

    def validate(self: Wrapper[T]) -> None:
        """Validates the value being wrapped."""
        pass
