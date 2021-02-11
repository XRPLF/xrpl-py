"""DOCSTRING"""
from dataclasses import dataclass

from xrpl.models.transactions.wrapper import Wrapper


# Should this subclass a wrapper? What do we think of that?
@dataclass(frozen=True)
class Hash256(Wrapper[str]):
    """A hash256."""

    # TODO: Add some validation
