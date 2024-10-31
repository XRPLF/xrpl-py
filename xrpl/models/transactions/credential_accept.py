"""Model for CredentialAccept transaction type."""

from dataclasses import dataclass, field
from typing import Dict, Optional

from typing_extensions import Self

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import HEX_REGEX, KW_ONLY_DATACLASS, require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class CredentialAccept(Transaction):
    """This transaction accepts a credential issued to the Account (i.e. the Account is
    the Subject of the Credential object). The credential is not considered valid until
    it has been transferred/accepted.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.CREDENTIAL_ACCEPT,
        init=False,
    )

    account: str = REQUIRED  # type: ignore
    """
    The subject of the credential.
    """
    issuer: str = REQUIRED  # type: ignore
    """
    The issuer of the credential.
    """

    credential_type: str = REQUIRED  # type: ignore
    """
    A (hex-encoded) value to identify the type of credential from the issuer.
    """

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()
        if cred_type_error := self._get_credential_type_error() is not None:
            errors["credential_type"] = cred_type_error  # type: ignore
        return errors

    def _get_credential_type_error(self: Self) -> Optional[str]:
        errors = []
        if len(self.credential_type) == 0:
            errors.append("Length must be > 0.")
        if len(self.credential_type) > 128:
            errors.append("Length must be < 128.")
        if not bool(HEX_REGEX.fullmatch(self.credential_type)):
            errors.append("credential_type field must be encoded in base-16 format.")
        return " ".join(errors) if errors else None
