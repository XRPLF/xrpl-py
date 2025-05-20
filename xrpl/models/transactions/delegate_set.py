"""Model for DelegateSet transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Union

from typing_extensions import Self

from xrpl.models.nested_model import NestedModel
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init

PERMISSIONS_MAX_LENGTH = 10

NON_DELEGABLE_TRANSACTIONS = {
    TransactionType.ACCOUNT_SET,
    TransactionType.SET_REGULAR_KEY,
    TransactionType.SIGNER_LIST_SET,
    TransactionType.DELEGATE_SET,
    TransactionType.ACCOUNT_DELETE,
    TransactionType.BATCH,
}


class GranularPermission(str, Enum):
    """
    These permissions would support control over some smaller portion of a transaction,
    rather than being able to do all of the functionality that the transaction allows.
    """

    TRUSTLINE_AUTHORIZE = "TrustlineAuthorize"
    """Authorize a trustline."""

    TRUSTLINE_FREEZE = "TrustlineFreeze"
    """Freeze a trustline."""

    TRUSTLINE_UNFREEZE = "TrustlineUnfreeze"
    """Unfreeze a trustline."""

    ACCOUNT_DOMAIN_SET = "AccountDomainSet"
    """Modify the domain of an account."""

    ACCOUNT_EMAIL_HASH_SET = "AccountEmailHashSet"
    """Modify the EmailHash of an account."""

    ACCOUNT_MESSAGE_KEY_SET = "AccountMessageKeySet"
    """Modify the MessageKey of an account."""

    ACCOUNT_TRANSFER_RATE_SET = "AccountTransferRateSet"
    """Modify the transfer rate of an account."""

    ACCOUNT_TICK_SIZE_SET = "AccountTickSizeSet"
    """Modify the tick size of an account."""

    PAYMENT_MINT = "PaymentMint"
    """Send a payment for a currency where the sending account is the issuer."""

    PAYMENT_BURN = "PaymentBurn"
    """Send a payment for a currency where the destination account is the issuer."""

    MPTOKEN_ISSUANCE_LOCK = "MPTokenIssuanceLock"
    """Use the MPTIssuanceSet transaction to lock (freeze) a holder."""

    MPTOKEN_ISSUANCE_UNLOCK = "MPTokenIssuanceUnlock"
    """Use the MPTIssuanceSet transaction to unlock (unfreeze) a holder."""


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class Permission(NestedModel):
    """Represents one entry in a Permissions list used in DelegateSet
    transaction.
    """

    permission_value: Union[
        TransactionType, GranularPermission
    ] = REQUIRED  # type: ignore
    """
    Transaction level or granular permission.

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
    """The transaction permissions that the authorized account has been granted."""

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
        if len(self.permissions) > PERMISSIONS_MAX_LENGTH:
            return (
                f"Length of `permissions` list is greater than "
                f"{PERMISSIONS_MAX_LENGTH}."
            )

        entered_permissions = [
            permission.permission_value for permission in self.permissions
        ]
        if len(entered_permissions) != len(set(entered_permissions)):
            return "Duplicate permission value in `permissions` list."

        if set(entered_permissions) & NON_DELEGABLE_TRANSACTIONS:
            return (
                f"Non-delegable transactions found in `permissions` list: "
                f"{set(entered_permissions) & NON_DELEGABLE_TRANSACTIONS}."
            )

        return None
