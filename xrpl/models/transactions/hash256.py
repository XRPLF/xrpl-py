"""DOCSTRING"""
from __future__ import annotations

from dataclasses import dataclass

from xrpl.models.exceptions import XRPLModelValidationException
from xrpl.models.transactions.wrapper import Wrapper


@dataclass(frozen=True)
class Hash256(Wrapper[str]):
    """A hash256."""

    def __eq__(self: Hash256, object: object) -> bool:
        """Evaluates whether or not two Hash256s are equal."""
        # Convert to uppercase so we can ignore casing in our comparison.
        uppercased_value = self.value.upper()
        if isinstance(object, str):
            return uppercased_value == object.upper()

        if isinstance(object, Hash256):
            return uppercased_value == object.value.upper()

        raise XRPLModelValidationException("Can only compare with another Hash256.")
