"""Model for MPTokenAuthorize transaction type."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.mptoken_authorize_flag import MPTokenAuthorizeFlag
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class MPTokenAuthorize(Transaction):
    """
    This transaction enables an account to hold an amount of a particular MPT issuance. When
    applied successfully, it creates a new MPToken object with an initial zero balance,
    owned by the holder account.  If the issuer has set lsfMPTRequireAuth (allow-listing) on
    the MPTokenIssuance, the issuer must submit an MPTokenAuthorize transaction as well in
    order to give permission to the holder. If lsfMPTRequireAuth is not set and the issuer
    attempts to submit this transaction, it will fail.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.MPTOKEN_AUTHORIZE,
        init=False
    )

    mp_token_issuance_id: str = REQUIRED
    """
    Indicates the ID of the MPT involved.
    """

    holder: Optional[str] = None
    """
    (Optional) Specifies the holder's address that the issuer wants to authorize. Only used
    for authorization/allow-listing; must be empty if submitted by the holder.
    """

class MPTokenAuthorizeFlagInterface(FlagInterface):
    """
    Enum for MPTokenAuthorize Transaction Flags.
    """

    TF_MPT_UNAUTHORIZE: bool

class MPTokenAuthorizeFlag(int, Enum):
    """
    Enum for MPTokenAuthorize Transaction Flags.
    """

    TF_MPT_UNAUTHORIZE = 0x00000001
    """
    If set, and transaction is submitted by a holder, it indicates that the holder no longer wants to
hold the MPToken, which will be deleted as a result. If the holder&#39;s MPToken has a non-zero balance
while trying to set this flag, the transaction fails. On the other hand, if set, and transaction is
submitted by an issuer, it would mean that the issuer wants to unauthorize the holder (only applicable
for allow-listing), which would unset the lsfMPTAuthorized flag on the MPToken.

    """


