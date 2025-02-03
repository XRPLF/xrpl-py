"""Model for PermissionedDomainDelete transaction type."""

from dataclasses import dataclass, field

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


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
