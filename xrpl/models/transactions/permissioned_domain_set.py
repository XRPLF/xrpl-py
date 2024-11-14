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
    """Represents a PermissionedDomainSet transaction"""

    domain_id: Optional[str] = None

    accepted_credentials: List[Credential] = REQUIRED  # type: ignore

    transaction_type: TransactionType = field(
        default=TransactionType.PERMISSIONED_DOMAIN_SET,
        init=False,
    )

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()

        def _validate_credentials_length(
            credentials: List[Credential], field_name: str
        ) -> None:
            if len(credentials) == 0:
                errors["PermissionedDomainSet"] = f"{field_name} list cannot be empty."
            elif len(credentials) > _MAX_ACCEPTED_CREDENTIALS_LENGTH:
                errors["PermissionedDomainSet"] = (
                    f"{field_name} list cannot have more than "
                    + f"{_MAX_ACCEPTED_CREDENTIALS_LENGTH} elements."
                )

            if len(credentials) != len(set(credentials)):
                errors["PermissionedDomainSet"] = (
                    f"{field_name} list cannot contain duplicate credentials."
                )

        _validate_credentials_length(self.accepted_credentials, "AcceptedCredentials")

        return errors
