"""DOCSTRING"""
from typing import Generic, TypeVar

T = TypeVar("T")


class Wrapper(Generic[T]):
    """A typed wrapper for single values."""

    value: T
