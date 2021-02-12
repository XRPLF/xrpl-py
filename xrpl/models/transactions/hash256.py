"""DOCSTRING"""
from __future__ import annotations

from dataclasses import dataclass

from xrpl.models.exceptions import XRPLModelValidationException
from xrpl.models.transactions.wrapper import Wrapper


# Should this subclass a wrapper? What do we think of that?
@dataclass(frozen=True)
class Hash256(Wrapper):
    """A hash256."""

    # TODO: Add some validation
    # TODO: Can this be genericized somehow?
    def __eq__(self: Hash256, object: object) -> bool:
        """Evaluates whether or not two Hash256s are equal."""
        # TODO: Uppercase?
        # if isinstance(object, str):
        #     return self.value == object

        if isinstance(object, Hash256):
            return self.value == object.value

        raise XRPLModelValidationException("Can only compare with another Hash256.")
