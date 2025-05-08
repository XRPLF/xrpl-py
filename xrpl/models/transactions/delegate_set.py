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

PERMISSION_MAX_LENGTH = 10


class DelegatableTransaction(str, Enum):
    """Transaction type that are delegatable using DelegateSet transaction."""

    AMM_BID = "AMMBid"
    AMM_CREATE = "AMMCreate"
    AMM_CLAWBACK = "AMMClawback"
    AMM_DELETE = "AMMDelete"
    AMM_DEPOSIT = "AMMDeposit"
    AMM_VOTE = "AMMVote"
    AMM_WITHDRAW = "AMMWithdraw"
    CHECK_CANCEL = "CheckCancel"
    CHECK_CASH = "CheckCash"
    CHECK_CREATE = "CheckCreate"
    CLAWBACK = "Clawback"
    CREDENTIAL_ACCEPT = "CredentialAccept"
    CREDENTIAL_CREATE = "CredentialCreate"
    CREDENTIAL_DELETE = "CredentialDelete"
    DEPOSIT_PREAUTH = "DepositPreauth"
    DID_DELETE = "DIDDelete"
    DID_SET = "DIDSet"
    ESCROW_CANCEL = "EscrowCancel"
    ESCROW_CREATE = "EscrowCreate"
    ESCROW_FINISH = "EscrowFinish"
    MPTOKEN_AUTHORIZE = "MPTokenAuthorize"
    MPTOKEN_ISSUANCE_CREATE = "MPTokenIssuanceCreate"
    MPTOKEN_ISSUANCE_DESTROY = "MPTokenIssuanceDestroy"
    MPTOKEN_ISSUANCE_SET = "MPTokenIssuanceSet"
    NFTOKEN_ACCEPT_OFFER = "NFTokenAcceptOffer"
    NFTOKEN_BURN = "NFTokenBurn"
    NFTOKEN_CANCEL_OFFER = "NFTokenCancelOffer"
    NFTOKEN_CREATE_OFFER = "NFTokenCreateOffer"
    NFTOKEN_MINT = "NFTokenMint"
    NFTOKEN_MODIFY = "NFTokenModify"
    OFFER_CANCEL = "OfferCancel"
    OFFER_CREATE = "OfferCreate"
    ORACLE_SET = "OracleSet"
    ORACLE_DELETE = "OracleDelete"
    PAYMENT = "Payment"
    PAYMENT_CHANNEL_CLAIM = "PaymentChannelClaim"
    PAYMENT_CHANNEL_CREATE = "PaymentChannelCreate"
    PAYMENT_CHANNEL_FUND = "PaymentChannelFund"
    PERMISSIONED_DOMAIN_SET = "PermissionedDomainSet"
    PERMISSIONED_DOMAIN_DELETE = "PermissionedDomainDelete"
    TICKET_CREATE = "TicketCreate"
    TRUST_SET = "TrustSet"
    XCHAIN_ACCOUNT_CREATE_COMMIT = "XChainAccountCreateCommit"
    XCHAIN_ADD_ACCOUNT_CREATE_ATTESTATION = "XChainAddAccountCreateAttestation"
    XCHAIN_ADD_CLAIM_ATTESTATION = "XChainAddClaimAttestation"
    XCHAIN_CLAIM = "XChainClaim"
    XCHAIN_COMMIT = "XChainCommit"
    XCHAIN_CREATE_BRIDGE = "XChainCreateBridge"
    XCHAIN_CREATE_CLAIM_ID = "XChainCreateClaimID"
    XCHAIN_MODIFY_BRIDGE = "XChainModifyBridge"


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
        DelegatableTransaction, GranularPermission
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
        if len(self.permissions) > PERMISSION_MAX_LENGTH:
            return (
                f"Length of `permissions` list is greater than {PERMISSION_MAX_LENGTH}."
            )

        if len(self.permissions) != len(set(self.permissions)):
            return "Duplicate permission value in `permissions` list."

        return None
