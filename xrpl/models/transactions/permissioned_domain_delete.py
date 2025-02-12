"""Model for PermissionedDomainDelete transaction type."""

import re
from dataclasses import dataclass, field
from typing import Dict, Final, Pattern

from typing_extensions import Self

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init

_DOMAIN_ID_REGEX: Final[Pattern[str]] = re.compile("[A-F0-9]{64}")
DOMAIN_ID_LENGTH: Final[int] = 64


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class PermissionedDomainDelete(Transaction):
    """This transaction deletes a PermissionedDomain object."""

    domain_id: str = REQUIRED  # type: ignore
    """The domain to delete."""

    transaction_type: TransactionType = field(
        default=TransactionType.PERMISSIONED_DOMAIN_DELETE,
        init=False,
    )
    """The transaction type (PermissionedDomainDelete)."""

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()

        if len(self.domain_id) != DOMAIN_ID_LENGTH:
            errors["PermissionedDomainDelete"] = (
                f"domain_id must be {DOMAIN_ID_LENGTH} characters long."
            )
        elif not _DOMAIN_ID_REGEX.fullmatch(self.domain_id):
            errors["PermissionedDomainDelete"] = (
                "domain_id does not conform to hex format."
            )

        return errors
