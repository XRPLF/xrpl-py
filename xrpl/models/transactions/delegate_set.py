"""Model for DelegateSet transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from typing_extensions import Self

from xrpl.models.nested_model import NestedModel
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init

PERMISSION_MAX_LENGTH = 10

"""
This is a utility map of granular permission-names to their UINT32 integer values. This
can be used to specify the inputs for `Permission` inner-object (defined below).
"""
GRANULAR_PERMISSIONS = {
    "TrustlineAuthorize": 65537,
    "TrustlineFreeze": 65538,
    "TrustlineUnfreeze": 65539,
    "AccountDomainSet": 65540,
    "AccountEmailHashSet": 65541,
    "AccountMessageKeySet": 65542,
    "AccountTransferRateSet": 65543,
    "AccountTickSizeSet": 65544,
    "PaymentMint": 65545,
    "PaymentBurn": 65546,
    "MPTokenIssuanceLock": 65547,
    "MPTokenIssuanceUnlock": 65548,
}


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class Permission(NestedModel):
    """Represents one entry in a Permissions list used in DelegateSet
    transaction.
    """

    permission_value: int = REQUIRED  # type: ignore
    """
    Integer representation of the transaction-level or granular permission.

    :meta hide-value:
    """


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class DelegateSet(Transaction):
    """DelegateSet allows an account to delegate a set of permissions to another
    account.
    """

    authorize: str = REQUIRED  # type: ignore
    """The authorized account."""

    permissions: List[Permission] = REQUIRED  # type: ignore
    """The transaction permissions that the account has been granted."""

    transaction_type: TransactionType = field(
        default=TransactionType.DELEGATE_SET,
        init=False,
    )
    """The transaction type (DelegateSet)."""

    def _get_errors(self: Self) -> Dict[str, str]:
        return {
            key: value
            for key, value in {
                **super()._get_errors(),
                "permissions": self._get_permissions_error(),
                "account_addresses": self._validate_account_addresses(),
            }.items()
            if value is not None
        }

    def _validate_account_addresses(self: Self) -> Optional[str]:
        if self.authorize == self.account:
            return "Field `authorize` and `account` must be different."
        return None

    def _get_permissions_error(self: Self) -> Optional[str]:
        if len(self.permissions) > PERMISSION_MAX_LENGTH:
            return (
                f"Length of `permissions` list is greater than {PERMISSION_MAX_LENGTH}."
            )

        permission_unique_values = set()
        for permission in self.permissions:
            if permission.permission_value in permission_unique_values:
                return "Duplicate permission value in `permissions` list."
            permission_unique_values.add(permission.permission_value)
        return None
