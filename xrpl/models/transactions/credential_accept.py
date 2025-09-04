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
class CredentialAccept(Transaction):
    """
    Represents a `CredentialCreate <https://xrpl.org/docs/references/protocol/transactions/types/credentialaccept>`_ transaction,
    which accepts a Credential object. A Credential object is a credential that can be used to verify the identity of a subject.
    """

    Issuer: str = REQUIRED  # type: ignore
    """
    The address of the issuer that created the credential.
    """

    CredentialType: str = REQUIRED  # type: ignore
    """
    Arbitrary data defining the type of credential this entry represents.
    The minimum length is 1 byte and the maximum length is 64 bytes.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.CREDENTIAL_ACCEPT,
        init=False,
    )
