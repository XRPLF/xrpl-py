"""Model for CredentialCreate transaction type."""

from dataclasses import dataclass, field
from typing import Dict, Optional

from typing_extensions import Self

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import HEX_REGEX, KW_ONLY_DATACLASS, require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class CredentialCreate(Transaction):
    """This transaction creates a Credential object. It must be sent by the issuer."""

    transaction_type: TransactionType = field(
        default=TransactionType.CREDENTIAL_CREATE,
        init=False,
    )

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
    A (hex-encoded) value to identify the type of credential from the issuer.
    """
    expiration: Optional[int] = None
    """
    Optional credential expiration.
    """
    uri: Optional[str] = None
    """
    Optional additional data about the credential (such as a link to the Verifiable
    Credential document).
    """

    def _get_errors(self: Self) -> Dict[str, str]:
        return {
            key: value
            for key, value in {
                **super()._get_errors(),
                "uri": self._get_uri_error(),
                "credential_type": self._get_credential_type_error(),
            }.items()
            if value is not None
        }

    def _get_uri_error(self: Self) -> Optional[str]:
        if self.uri is not None:
            error = ""
            if len(self.uri) == 0:
                error += "Length must be > 0. "
            if len(self.uri) > 256:
                error += "Length of URI field must not be greater than 256 characters. "
            if not HEX_REGEX.fullmatch(self.uri):
                error += "URI field must be encoded in base-16 format. "
            return error if error != "" else None
        return None

    def _get_credential_type_error(self: Self) -> Optional[str]:
        error = ""
        # credential_type is a required field in this transaction
        if len(self.credential_type) == 0:
            error += "Length of credential_type field must be greater than 0. "
        if len(self.credential_type) > 64:
            error += (
                "Length of credential_type field must not be greater than 64 bytes. "
            )
        if not HEX_REGEX.fullmatch(self.credential_type):
            error += "credential_type field must be encoded in base-16 format. "
        return error if error != "" else None
