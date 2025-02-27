"""Model for PermissionedDomainSet transaction type."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from typing_extensions import Self

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.deposit_preauth import Credential
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init

_MAX_ACCEPTED_CREDENTIALS_LENGTH = 10


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class PermissionedDomainSet(Transaction):
    """This transaction creates or modifies a PermissionedDomain object."""

    domain_id: Optional[str] = None
    """The domain to modify. Must be included if modifying an existing domain."""

    accepted_credentials: List[Credential] = REQUIRED  # type: ignore
    """The credentials that are accepted by the domain. Ownership of one of these
    credentials automatically makes you a member of the domain. An empty array means
    deleting the field."""

    transaction_type: TransactionType = field(
        default=TransactionType.PERMISSIONED_DOMAIN_SET,
        init=False,
    )
    """The transaction type (PermissionedDomainSet)."""

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()

        if len(self.accepted_credentials) == 0:
            errors["PermissionedDomainSet"] = (
                "AcceptedCredentials list cannot be empty."
            )
        elif len(self.accepted_credentials) > _MAX_ACCEPTED_CREDENTIALS_LENGTH:
            errors["PermissionedDomainSet"] = (
                "AcceptedCredentials list cannot have more than "
                + f"{_MAX_ACCEPTED_CREDENTIALS_LENGTH} elements."
            )
        elif len(self.accepted_credentials) != len(set(self.accepted_credentials)):
            errors["PermissionedDomainSet"] = (
                "AcceptedCredentials list cannot contain duplicate credentials."
            )

        return errors
