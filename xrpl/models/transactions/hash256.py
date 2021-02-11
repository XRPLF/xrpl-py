"""DOCSTRING"""
from dataclasses import dataclass


# Should this subclass a wrapper? What do we think of that?
@dataclass(frozen=True)
class Hash256:
    """A hash256."""

    value: str
