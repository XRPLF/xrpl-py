"""Model for the CredentialDelete transaction"""

from dataclasses import dataclass, field
from typing import Dict, Optional

from typing_extensions import Self

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import HEX_REGEX, KW_ONLY_DATACLASS, require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class CredentialDelete(Transaction):
    """This transaction deletes a Credential object."""

    transaction_type: TransactionType = field(
        default=TransactionType.CREDENTIAL_DELETE, init=False
    )
    """
    The transaction type (CredentialDelete).
    """

    account: str = REQUIRED  # type: ignore
    """The transaction submitter."""

    subject: Optional[str] = None
    """The person that the credential is for. If omitted, Account is assumed to be the
    subject."""

    issuer: Optional[str] = None
    """The issuer of the credential. If omitted, Account is assumed to be the issuer."""

    credential_type: str = REQUIRED  # type: ignore
    """A (hex-encoded) value to identify the type of credential from the issuer."""

    def _get_errors(self: Self) -> Dict[str, str]:
        errors: Dict[str, str] = {
            key: value
            for key, value in {
                **super()._get_errors(),
                "credential_type": self._get_credential_type_error(),
            }.items()
            if value is not None
        }

        if not self.subject and not self.issuer:
            errors[
                "invalid_params"
            ] = "CredentialDelete transaction: Neither `issuer` nor `subject` provided."

        return errors

    def _get_credential_type_error(self: Self) -> Optional[str]:
        errors = []
        # credential_type is a required field in this transaction
        if len(self.credential_type) == 0:
            errors.append("Length must be > 0.")
        if len(self.credential_type) > 128:
            errors.append("Length must be < 128.")
        if not bool(HEX_REGEX.fullmatch(self.credential_type)):
            errors.append("credential_type field must be encoded in hex.")
        return " ".join(errors) if errors else None
