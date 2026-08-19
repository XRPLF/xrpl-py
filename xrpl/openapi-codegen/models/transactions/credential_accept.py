"""Model for CredentialAccept transaction type."""

from dataclasses import dataclass, field
from typing import Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class CredentialAccept(Transaction):
    """
    A CredentialAccept transaction accepts a credential, which makes the credential valid.
    Only the subject of the credential can do this.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.CREDENTIAL_ACCEPT, init=False
    )

    credential_type: str = REQUIRED
    """
    Arbitrary data defining the type of credential. The minimum size is 1 byte and the
    maximum is 64 bytes.
    """

    issuer: str = REQUIRED
    """
    The address of the issuer that created the credential.
    """

    def _get_errors(self: CredentialAccept) -> Dict[str, str]:
        errors = super._get_errors()
        if self.credential_type is not None and len(self.credential_type) < 1:
            errors["CredentialAccept"] = (
                "Field `credential_type` must have a length greater than or equal to 1"
            )
        if self.credential_type is not None and len(self.credential_type) > 128:
            errors["CredentialAccept"] = (
                "Field `credential_type` must have a length less than or equal to 128"
            )
        return errors
