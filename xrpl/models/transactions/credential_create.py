"""Model for CredentialCreate transaction type."""

from dataclasses import dataclass, field
from typing import Dict, Optional

from typing_extensions import Self

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import (
    HEX_REGEX,
    KW_ONLY_DATACLASS,
    get_credential_type_error,
    require_kwargs_on_init,
)

_MAX_URI_LENGTH = 256


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class CredentialCreate(Transaction):
    """This transaction creates a Credential object. It must be sent by the issuer."""

    account: str = REQUIRED  # type: ignore
    """
    The issuer of the credential.
    """

    subject: str = REQUIRED  # type: ignore
    """
    The subject of the credential.
    """

    credential_type: str = REQUIRED  # type: ignore
    """
    A hex-encoded value to identify the type of credential from the issuer.
    """

    expiration: Optional[int] = None
    """
    The credential expiration.
    """

    uri: Optional[str] = None
    """
    Additional data about the credential (such as a link to the Verifiable
    Credential document).
    """

    transaction_type: TransactionType = field(
        default=TransactionType.CREDENTIAL_CREATE,
        init=False,
    )

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()

        if (uri_error := self._get_uri_error()) is not None:
            errors["uri"] = uri_error

        if (
            cred_type_error := get_credential_type_error(self.credential_type)
        ) is not None:
            errors["credential_type"] = cred_type_error

        return errors

    def _get_uri_error(self: Self) -> Optional[str]:
        if self.uri is None:
            return None

        errors = []
        if len(self.uri) == 0:
            errors.append("cannot be an empty string.")
        elif len(self.uri) > _MAX_URI_LENGTH:
            errors.append(f"Length cannot exceed {_MAX_URI_LENGTH} characters.")

        if not HEX_REGEX.fullmatch(self.uri):
            errors.append("Must be encoded in hex.")
        return " ".join(errors) if errors else None
