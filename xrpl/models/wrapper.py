"""A generic, immutable wrapper to wrap single value models in the XRPL."""

import abc
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class Wrapper(abc.ABC, Generic[T]):
    """A generic, immutable wrapper to wrap single value models in the XRPL."""

    value: T
