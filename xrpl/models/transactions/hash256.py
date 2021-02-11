"""DOCSTRING"""
from __future__ import annotations

from dataclasses import dataclass

from xrpl.models.exceptions import XRPLModelValidationException
from xrpl.models.transactions.wrapper import Wrapper


# Should this subclass a wrapper? What do we think of that?
@dataclass(frozen=True)
class Hash256(Wrapper[str]):
    """A hash256."""

    # TODO: Add some validation

    def __eq__(self: Hash256, object: object) -> bool:
        """Evaluates whether or not two Hash256s are equal."""
        if not isinstance(object, Hash256):
            raise XRPLModelValidationException("Can only compare with another Hash256.")

        # TODO: uppercase since these are magic strings?
        return self.value == object.value
