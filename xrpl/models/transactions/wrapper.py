"""DOCSTRING"""
from abc import ABC
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class Wrapper(ABC, Generic[T]):
    """A typed wrapper for single values."""

    value: T
