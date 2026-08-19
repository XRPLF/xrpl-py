"""Model for MPTokenIssuanceCreate transaction type."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.mptoken_issuance_create_flag import MPTokenIssuanceCreateFlag
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class MPTokenIssuanceCreate(Transaction):
    """
    The MPTokenIssuanceCreate transaction creates an MPTokenIssuance object and adds it to
    the relevant directory node of the creator account. This transaction is the only
    opportunity an issuer has to specify any token fields that are defined as immutable (for
    example, MPT Flags).  If the transaction is successful, the newly created token is owned
    by the account (the creator account) that executed the transaction.  Whenever your query
    returns an MPTokenIssuance transaction response, there will always be an mpt_issuance_id
    field on the Transaction Metadata page.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.MPTOKEN_ISSUANCE_CREATE, init=False
    )

    asset_scale: Optional[int] = None
    """
    (Optional) An asset scale is the difference, in orders of magnitude, between a standard
    unit and a corresponding fractional unit. More formally, the asset scale is a
    non-negative integer (0, 1, 2, …) such that one standard unit equals 10^(-scale) of a
    corresponding fractional unit. If the fractional unit equals the standard unit, then the
    asset scale is 0. Note that this value is optional, and will default to 0 if not
    supplied.
    """

    transfer_fee: Optional[int] = None
    """
    (Optional) The value specifies the fee to be charged by the issuer for secondary sales
    of the Token, if such sales are allowed. Valid values for this field are between 0 and
    50,000 inclusive, allowing transfer rates of between 0.000% and 50.000% in increments of
    0.001. The field must not be present if the tfMPTCanTransfer flag is not set. If it is,
    the transaction should fail and a fee should be claimed.
    """

    maximum_amount: Optional[str] = None
    """
    (Optional) The maximum asset amount of this token that can ever be issued, as a base-10
    number encoded as a string. The current default maximum limit is
    9,223,372,036,854,775,807 (2^63-1). This limit may increase in the future. If an upper
    limit is required, you must specify this field.
    """

    mp_token_metadata: Optional[str] = None
    """
    Arbitrary metadata about this issuance, in hex format. The limit for this field is 1024
    bytes.
    """

    def _get_errors(self: MPTokenIssuanceCreate) -> Dict[str, str]:
        errors = super._get_errors()
        # This check is only applicable if the flag belongs to the `flags` field inherited from base Transaction.
        # For other cases such as `set_flag` or `clear_flag` field in account_info transaction, please fix accordingly.
        if (
            not self.has_flag(MPTokenIssuanceCreateFlag.TF_MPT_CAN_TRANSFER)
            and self.transfer_fee is not None
        ):
            errors["MPTokenIssuanceCreate"] = (
                "`transfer_fee` must not be set without flag `TF_MPT_CAN_TRANSFER`"
            )
        if self.transfer_fee is not None and self.transfer_fee < 0:
            errors["MPTokenIssuanceCreate"] = (
                "Field `transfer_fee` must have a value greater than or equal to 0"
            )
        if self.transfer_fee is not None and self.transfer_fee > 50000:
            errors["MPTokenIssuanceCreate"] = (
                "Field `transfer_fee` must have a value less than or equal to 50000"
            )
        if self.mp_token_metadata is not None and len(self.mp_token_metadata) < 1:
            errors["MPTokenIssuanceCreate"] = (
                "Field `mp_token_metadata` must have a length greater than or equal to 1"
            )
        return errors


class MPTokenIssuanceCreateFlagInterface(FlagInterface):
    """
    Enum for MPTokenIssuanceCreate Transaction Flags.
    """

    TF_MPT_CAN_LOCK: bool
    TF_MPT_REQUIRE_AUTH: bool
    TF_MPT_CAN_ESCROW: bool
    TF_MPT_CAN_TRADE: bool
    TF_MPT_CAN_TRANSFER: bool
    TF_MPT_CAN_CLAWBACK: bool


class MPTokenIssuanceCreateFlag(int, Enum):
    """
    Enum for MPTokenIssuanceCreate Transaction Flags.
    """

    TF_MPT_CAN_LOCK = 0x00000002
    """
    If set, indicates that the MPT can be locked both individually and globally. If not set, the MPT cannot be locked in any way.
    """

    TF_MPT_REQUIRE_AUTH = 0x00000004
    """
    If set, indicates that individual holders must be authorized. This enables issuers to limit who can hold their assets.
    """

    TF_MPT_CAN_ESCROW = 0x00000008
    """
    If set, indicates that individual holders can place their balances into an escrow.
    """

    TF_MPT_CAN_TRADE = 0x00000010
    """
    If set, indicates that individual holders can trade their balances using the XRP Ledger DEX.
    """

    TF_MPT_CAN_TRANSFER = 0x00000020
    """
    If set, indicates that tokens can be transferred to other accounts that are not the issuer.
    """

    TF_MPT_CAN_CLAWBACK = 0x00000040
    """
    If set, indicates that the issuer can use the Clawback transaction to claw back value from individual holders.
    """
