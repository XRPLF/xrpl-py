"""Model for CheckCreate transaction type."""

from dataclasses import dataclass, field
from typing import Optional

from xrpl.models.amounts import Amount
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class CredentialCreate(Transaction):
    """
    Represents a `CredentialCreate <https://xrpl.org/docs/references/protocol/transactions/types/credentialcreate>`_ transaction,
    which creates a Credential object. A Credential object is a credential that can be used to verify the identity of a subject.
    """

    Subject: str = REQUIRED  # type: ignore
    """
    The subject of the credential.
    """

    CredentialType: str = REQUIRED  # type: ignore
    """
    Arbitrary data defining the type of credential this entry represents.
    The minimum length is 1 byte and the maximum length is 64 bytes.
    """

    Expiration: Optional[int] = None
    """
    Time after which this credential expires, in seconds since the Ripple Epoch.
    """

    url: Optional[str] = None
    """
    Arbitrary additional data about the credential, such as the URL where users can look up an
    associated Verifiable Credential document. If present,
    the minimum length is 1 byte and the maximum is 256 bytes.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.CREDENTIAL_CREATE,
        init=False,
    )
