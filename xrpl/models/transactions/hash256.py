"""A wrapped string containing the Hex representation of a 256-bit Hash."""
from __future__ import annotations

from dataclasses import dataclass

from xrpl.models.exceptions import XRPLModelValidationException
from xrpl.models.transactions.wrapper import Wrapper

_HASH256_LENGTH = 64


@dataclass(frozen=True)
class Hash256(Wrapper[str]):
    """A wrapped string containing the Hex representation of a 256-bit Hash."""

    def validate(self: Wrapper) -> None:
        """
        Validates whether or not the wrapped value is a valid Hash256.

        Raises:
            XRPLModelValidationException: if the value being wrapped cannot be
                validated.
        """
        if len(self.value) != _HASH256_LENGTH:
            raise XRPLModelValidationException("Hash256 must have 64 characters.")

    def __eq__(self: Hash256, object: object) -> bool:
        """Evaluates whether or not two Hash256s are equal."""
        # Convert to uppercase so we can ignore casing in our comparison.
        uppercased_value = self.value.upper()
        if isinstance(object, str):
            return uppercased_value == object.upper()

        if isinstance(object, Hash256):
            return uppercased_value == object.value.upper()

        raise XRPLModelValidationException("Can only compare with another Hash256.")
