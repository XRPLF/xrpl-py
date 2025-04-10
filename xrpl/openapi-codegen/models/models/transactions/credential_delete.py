"""Model for CredentialDelete transaction type."""
from dataclasses import dataclass, field
from typing import Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class CredentialDelete(Transaction):
    """
    A CredentialDelete transaction removes a credential from the ledger, effectively
    revoking it.  Users may also want to delete an unwanted credential to reduce their
    reserve requirement.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.CREDENTIAL_DELETE,
        init=False
    )

    credential_type: str = REQUIRED
    """
    Arbitrary data defining the type of credential to delete. The minimum length is 1 byte
    and the maximum length is 256 bytes.
    """

    subject: Optional[str] = None
    """
    The subject of the credential to delete. If omitted, use the Account (sender of the
    transaction) as the subject of the credential.
    """

    issuer: Optional[str] = None
    """
    The issuer of the credential to delete. If omitted, use the Account (sender of the
    transaction) as the issuer of the credential.
    """

    def _get_errors(self: CredentialDelete) -> Dict[str, str]:
        errors = super._get_errors()
        if (
            self.subject is None and
            self.issuer is None
        ):
            errors["CredentialDelete"] = "At least one of `subject`, `issuer` must be set."
        if self.credential_type is not None and len(self.credential_type) < 1:
            errors["CredentialDelete"] = "Field `credential_type` must have a length greater than or equal to 1"
        if self.credential_type is not None and len(self.credential_type) > 128:
            errors["CredentialDelete"] = "Field `credential_type` must have a length less than or equal to 128"
        return errors


