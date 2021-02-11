"""DOCSTRING"""
from typing import Generic, TypeVar

T = TypeVar("T")


class Wrapper(Generic[T]):
    """DOCSTRING"""

    value: T
