"""Model for AccountSet transaction type."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.account_set_asf_flag import AccountSetAsfFlag
from xrpl.models.account_set_flag import AccountSetFlag
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class AccountSet(Transaction):
    """
    An AccountSet transaction modifies the properties of an account in the XRP Ledger.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.ACCOUNT_SET, init=False
    )

    clear_flag: Optional[AccountSetAsfFlag] = None
    """
    (Optional) Unique identifier of a flag to disable for this account.
    """

    domain: Optional[str] = None
    """
    (Optional) The domain that owns this account, as a string of hex representing the ASCII
    for the domain in lowercase. Cannot be more than 256 bytes in length.
    """

    email_hash: Optional[str] = None
    """
    (Optional) An arbitrary 128-bit value. Conventionally, clients treat this as the md5
    hash of an email address to use for displaying a Gravatar image.
    """

    message_key: Optional[str] = None
    """
    (Optional) Public key for sending encrypted messages to this account. To set the key, it
    must be exactly 33 bytes, with the first byte indicating the key type: 0x02 or 0x03 for
    secp256k1 keys, 0xED for Ed25519 keys. To remove the key, use an empty value.
    """

    nf_token_minter: Optional[str] = None
    """
    (Optional) Another account that can mint NFTokens for you. (Added by the
    NonFungibleTokensV1_1 amendment.)
    """

    set_flag: Optional[AccountSetAsfFlag] = None
    """
    (Optional) Integer flag to enable for this account.
    """

    transfer_rate: Optional[int] = None
    """
    (Optional) The fee to charge when users transfer this account's tokens, represented as
    billionths of a unit. Cannot be more than 2000000000 or less than 1000000000, except for
    the special case 0 meaning no fee.
    """

    tick_size: Optional[int] = None
    """
    (Optional) Tick size to use for offers involving a currency issued by this address. The
    exchange rates of those offers is rounded to this many significant digits. Valid values
    are 3 to 15 inclusive, or 0 to disable. (Added by the TickSize amendment.)
    """

    wallet_locator: Optional[str] = None
    """
    (Optional) An arbitrary 256-bit value. If specified, the value is stored as part of the
    account but has no inherent meaning or requirements.
    """

    wallet_size: Optional[int] = None
    """
    (Optional) Not used. This field is valid in AccountSet transactions but does nothing.
    """

    def _get_errors(self: AccountSet) -> Dict[str, str]:
        errors = super._get_errors()
        if self.set_flag is not None and self.set_flag == self.clear_flag:
            errors[AccountSet] = "set_flag must not be equal to clear_flag."
        # This check is only applicable if the flag belongs to the `flags` field inherited from base Transaction.
        # For other cases such as `set_flag` or `clear_flag` field in account_info transaction, please fix accordingly.
        if (
            self.has_flag(AccountSetFlag.ASF_AUTHORIZED_NFTOKEN_MINTER)
            and self.nftoken_minter is None
        ):
            errors["AccountSet"] = (
                "`nftoken_minter` must be set with flag `ASF_AUTHORIZED_NFTOKEN_MINTER`"
            )
        # This check is only applicable if the flag belongs to the `flags` field inherited from base Transaction.
        # For other cases such as `set_flag` or `clear_flag` field in account_info transaction, please fix accordingly.
        if (
            not self.has_flag(AccountSetFlag.ASF_AUTHORIZED_NFTOKEN_MINTER)
            and self.nftoken_minter is not None
        ):
            errors["AccountSet"] = (
                "`nftoken_minter` must not be set without flag `ASF_AUTHORIZED_NFTOKEN_MINTER`"
            )
        # This check is only applicable if the flag belongs to the `flags` field inherited from base Transaction.
        # For other cases such as `set_flag` or `clear_flag` field in account_info transaction, please fix accordingly.
        if (
            self.has_flag(AccountSetFlag.ASF_AUTHORIZED_NFTOKEN_MINTER)
            and self.nftoken_minter is not None
        ):
            errors["AccountSet"] = (
                "`nftoken_minter` must not be set with flag `ASF_AUTHORIZED_NFTOKEN_MINTER`"
            )
        if self.domain is not None and self.domain.lower() != self.domain:
            return f"domain {self.domain} is not lowercase"
        if self.domain is not None and len(self.domain) > 256:
            errors["AccountSet"] = (
                "Field `domain` must have a length less than or equal to 256"
            )
        if self.transfer_rate is not None and self.transfer_rate != 0:
            if self.transfer_rate < 1000000000:
                errors["AccountSet"] = (
                    "Field `transfer_rate` must have a value greater than or equal to 1000000000"
                )
            if self.transfer_rate > 2000000000:
                errors["AccountSet"] = (
                    "Field `transfer_rate` must have a value less than or equal to 2000000000"
                )
        if self.tick_size is not None and self.tick_size != 0:
            if self.tick_size < 3:
                errors["AccountSet"] = (
                    "Field `tick_size` must have a value greater than or equal to 3"
                )
            if self.tick_size > 15:
                errors["AccountSet"] = (
                    "Field `tick_size` must have a value less than or equal to 15"
                )
        return errors


class AccountSetFlagInterface(FlagInterface):
    """
    Enum for AccountSet Transaction Flags.
    """

    TF_REQUIRE_DEST_TAG: bool
    TF_OPTIONAL_DEST_TAG: bool
    TF_REQUIRE_AUTH: bool
    TF_OPTIONAL_AUTH: bool
    TF_DISALLOW_XRP: bool
    TF_ALLOW_XRP: bool


class AccountSetFlag(int, Enum):
    """
    Enum for AccountSet Transaction Flags.
    """

    TF_REQUIRE_DEST_TAG = 0x00010000
    """
    The same as SetFlag: asfRequireDest.
    """

    TF_OPTIONAL_DEST_TAG = 0x00020000
    """
    The same as ClearFlag: asfRequireDest.
    """

    TF_REQUIRE_AUTH = 0x00040000
    """
    The same as SetFlag: asfRequireAuth.
    """

    TF_OPTIONAL_AUTH = 0x00080000
    """
    The same as ClearFlag: asfRequireAuth.
    """

    TF_DISALLOW_XRP = 0x00100000
    """
    The same as SetFlag: asfDisallowXRP.
    """

    TF_ALLOW_XRP = 0x00200000
    """
    The same as ClearFlag: asfDisallowXRP.
    """


class AccountSetAsfFlag(int, Enum):
    """
    Enum for AccountSet Flags.
    """

    ASF_ACCOUNT_TXN_ID = 5
    """
    Track the ID of this account&#39;s most recent transaction. Required for AccountTxnID.
    """

    ASF_ALLOW_TRUSTLINE_CLAWBACK = 16
    """
    Allow account to claw back tokens it has issued. (Requires the Clawback amendment.)
    """

    ASF_AUTHORIZED_NFTOKEN_MINTER = 10
    """
    Enable to allow another account to mint non-fungible tokens (NFTokens) on this account&#39;s behalf.
    """

    ASF_DEFAULT_RIPPLE = 8
    """
    Enable rippling on this account&#39;s trust lines by default.
    """

    ASF_DEPOSIT_AUTH = 9
    """
    Enable Deposit Authorization on this account. (Added by the DepositAuth amendment.)
    """

    ASF_DISABLE_MASTER = 4
    """
    Disallow use of the master key pair. Can only be enabled if the account has configured another way to sign transactions.
    """

    ASF_DISALLOW_INCOMING_CHECK = 13
    """
    Block incoming Checks. (Requires the DisallowIncoming amendment.)
    """

    ASF_DISALLOW_INCOMING_NFTOKEN_OFFER = 12
    """
    Block incoming NFTokenOffers. (Requires the DisallowIncoming amendment.)
    """

    ASF_DISALLOW_INCOMING_PAY_CHAN = 14
    """
    Block incoming Payment Channels. (Requires the DisallowIncoming amendment.)
    """

    ASF_DISALLOW_INCOMING_TRUSTLINE = 15
    """
    Block incoming trust lines. (Requires the DisallowIncoming amendment.)
    """

    ASF_DISALLOW_XRP = 3
    """
    XRP should not be sent to this account. (Advisory; not enforced by the XRP Ledger protocol.)
    """

    ASF_GLOBAL_FREEZE = 7
    """
    Freeze all assets issued by this account.
    """

    ASF_NO_FREEZE = 6
    """
    Permanently give up the ability to freeze individual trust lines or disable Global Freeze.
    """

    ASF_REQUIRE_AUTH = 2
    """
    Require authorization for users to hold balances issued by this address.
    """

    ASF_REQUIRE_DEST = 1
    """
    Require a destination tag to send transactions to this account.
    """
