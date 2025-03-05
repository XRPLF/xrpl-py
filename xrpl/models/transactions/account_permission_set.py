"""Model for AccountPermissionSet transaction type."""

from __future__ import annotations  # Requires Python 3.7+

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from typing_extensions import Self

from xrpl.models.nested_model import NestedModel
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init

PERMISSION_MAX_SIZE = 10


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class Permission(NestedModel):
    """Represents one entry in a Permissions list used in AccountPermissionSet
    transaction.
    """

    permission_value: int = REQUIRED  # type: ignore
    """
    Integer representation of the transaction-level or granular permission.

    :meta hide-value:
    """


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class AccountPermissionSet(Transaction):
    """AccountPermissionSet allows an account to delegate a set of permissions to another account.
    """

    authorize: str = REQUIRED  # type: ignore
    """The authorized account."""
    permissions: List[Permission] = REQUIRED  # type: ignore
    """The transaction permissions that the account has been granted."""

    transaction_type: TransactionType = field(
        default=TransactionType.ACCOUNT_PERMISSION_SET,
        init=False,
    )
    """The transaction type (AccountPermissionSet)."""

    def _get_errors(self: Self) -> Dict[str, str]:
        return {
            key: value
            for key, value in {
                **super()._get_errors(),
                "permissions": self._get_permissions_error(),
            }.items()
            if value is not None
        }

    def _get_permissions_error(self: Self) -> Optional[str]:
        if len(self.permissions) > PERMISSION_MAX_SIZE:
            return (
                f"Length of `permissions` list is greater than {PERMISSION_MAX_SIZE}."
            )

        permission_unique_values = set()
        for permission in self.permissions:
            if permission.permission_value in permission_unique_values:
                return "Duplicate permission value in `permissions` list."
            permission_unique_values.add(permission.permission_value)
        return None
