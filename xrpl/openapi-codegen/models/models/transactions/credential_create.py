"""Model for CredentialCreate transaction type."""
from dataclasses import dataclass, field
from pydantic import StrictFloat, StrictInt
from typing import Optional, Union
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class CredentialCreate(Transaction):
    """
    A CredentialCreate transaction creates a credential in the ledger. The issuer of the
    credential uses this transaction to provisionally issue a credential. The credential is
    not valid until the subject of the credential accepts it with a CredentialAccept
    transaction.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.CREDENTIAL_CREATE,
        init=False
    )

    credential_type: str = REQUIRED
    """
    Arbitrary data defining the type of credential this entry represents. The minimum length
    is 1 byte and the maximum length is 64 bytes.
    """

    expiration: Union[StrictFloat, StrictInt] = REQUIRED
    """
    Time after which this credential expires, in seconds since the Ripple Epoch.
    """

    subject: str = REQUIRED
    """
    The subject of the credential.
    """

    uri: Optional[str] = None
    """
    Arbitrary additional data about the credential, such as the URL where users can look up
    an associated Verifiable Credential document.  If present, the minimum length is 1 byte
    and the maximum is 256 bytes.
    """

    def _get_errors(self: CredentialCreate) -> Dict[str, str]:
        errors = super._get_errors()
        if self.credential_type is not None and len(self.credential_type) < 1:
            errors["CredentialCreate"] = "Field `credential_type` must have a length greater than or equal to 1"
        if self.credential_type is not None and len(self.credential_type) > 128:
            errors["CredentialCreate"] = "Field `credential_type` must have a length less than or equal to 128"
        if self.uri is not None and len(self.uri) < 1:
            errors["CredentialCreate"] = "Field `uri` must have a length greater than or equal to 1"
        if self.uri is not None and len(self.uri) > 512:
            errors["CredentialCreate"] = "Field `uri` must have a length less than or equal to 512"
        return errors


