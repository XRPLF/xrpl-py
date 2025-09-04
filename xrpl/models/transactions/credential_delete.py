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
class CredentialDelete(Transaction):
    """
    Represents a `CredentialDelete <https://xrpl.org/docs/references/protocol/transactions/types/credentialdelete>`_ transaction,
    which deletes a Credential object. A Credential object is a credential that can be used to verify the identity of a subject.
    """

    CredentialType: str = REQUIRED  # type: ignore
    """
    Arbitrary data defining the type of credential this entry represents.
    The minimum length is 1 byte and the maximum length is 64 bytes.
    :meta hide-value:
    """

    Subject: Optional[str] = None
    """
    The subject of the credential.
    :meta hide-value:
    """

    Issuer: Optional[str] = REQUIRED  # type: ignore
    """
    The address of the issuer that created the credential.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.CREDENTIAL_DELETE,
        init=False,
    )
