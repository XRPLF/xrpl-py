"""Model for AccountSet transaction type."""
from __future__ import annotations  # Requires Python 3.7+

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional

from typing_extensions import Final

from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init

_MAX_TRANSFER_RATE: Final[int] = 2000000000
_MIN_TRANSFER_RATE: Final[int] = 1000000000
_SPECIAL_CASE_TRANFER_RATE: Final[int] = 0

_MIN_TICK_SIZE: Final[int] = 3
_MAX_TICK_SIZE: Final[int] = 15
_DISABLE_TICK_SIZE: Final[int] = 0


class AccountSetFlag(int, Enum):
    """
    There are several options which can be either enabled or disabled for an account.
    Account options are represented by different types of flags depending on the
    situation. The AccountSet transaction type has several "AccountSet Flags" (prefixed
    `asf`) that can enable an option when passed as the SetFlag parameter, or disable
    an option when passed as the ClearFlag parameter. This enum represents those
    options.

    `See AccountSet Flags <https://xrpl.org/accountset.html#accountset-flags>`_
    """

    ASF_ACCOUNT_TXN_ID = 5
    """
    Track the ID of this account's most recent transaction. Required for
    `AccountTxnID <https://xrpl.org/transaction-common-fields.html#accounttxnid>`_
    """

    ASF_DEFAULT_RIPPLE = 8
    """
    Enable `rippling
    <https://xrpl.org/rippling.html>`_ on this account's trust lines by default.
    """

    ASF_DEPOSIT_AUTH = 9
    """
    Enable `Deposit Authorization
    <https://xrpl.org/depositauth.html>`_ on this account.
    """

    ASF_DISABLE_MASTER = 4
    """
    Disallow use of the master key pair. Can only be enabled if the account has
    configured another way to sign transactions, such as a `Regular Key
    <https://xrpl.org/cryptographic-keys.html>`_ or a `Signer List
    <https://xrpl.org/multi-signing.html>`_.
    """

    ASF_DISALLOW_XRP = 3
    """XRP should not be sent to this account. (Enforced by client applications)"""

    ASF_GLOBAL_FREEZE = 7
    """
    `Freeze
    <https://xrpl.org/freezes.html>`_ all assets issued by this account.
    """

    ASF_NO_FREEZE = 6
    """
    Permanently give up the ability to `freeze individual trust lines or disable
    Global Freeze <https://xrpl.org/freezes.html>`_. This flag can never be disabled
    after being enabled.
    """

    ASF_REQUIRE_AUTH = 2
    """
    Require authorization for users to hold balances issued by this address. Can
    only be enabled if the address has no trust lines connected to it.
    """

    ASF_REQUIRE_DEST = 1
    """Require a destination tag to send transactions to this account."""


@require_kwargs_on_init
@dataclass(frozen=True)
class AccountSet(Transaction):
    """
    Represents an `AccountSet transaction <https://xrpl.org/accountset.html>`_,
    which modifies the properties of an account in the XRP Ledger.
    """

    clear_flag: Optional[int] = None
    """
    Disable a specific `AccountSet Flag
    <https://xrpl.org/accountset.html#accountset-flags>`_
    """

    domain: Optional[str] = None
    """Set the DNS domain of the account owner."""

    email_hash: Optional[str] = None
    """
    Set the MD5 Hash to be used for generating an avatar image for this
    account.
    """

    message_key: Optional[str] = None
    """Set a public key for sending encrypted messages to this account."""

    set_flag: Optional[int] = None
    """
    Enable a specific `AccountSet Flag
    <https://xrpl.org/accountset.html#accountset-flags>`_
    """

    transfer_rate: Optional[int] = None
    """
    Set the transfer fee to use for tokens issued by this account. See
    `TransferRate <https://xrpl.org/accountset.html#transferrate>`_ for
    details.
    """

    tick_size: Optional[int] = None
    """
    Set the tick size to use when trading tokens issued by this account in
    the decentralized exchange. See `Tick Size
    <https://xrpl.org/ticksize.html>`_ for details.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.ACCOUNT_SET,
        init=False,
    )

    def _get_errors(self: AccountSet) -> Dict[str, str]:
        errors = super()._get_errors()
        tick_size_error = self._tick_size_error()
        transfer_rate_error = self._transfer_rate_error()
        if tick_size_error is not None:
            errors["tick_size"] = tick_size_error
        if transfer_rate_error is not None:
            errors["transfer_rate"] = transfer_rate_error
        if self.domain is not None and self.domain.lower() != self.domain:
            errors["domain"] = f"Domain {self.domain} is not lowercase"
        if self.clear_flag is not None and self.clear_flag == self.set_flag:
            errors[
                "AccountSet"
            ] = f"Clear flag {self.clear_flag} is equal to set flag {self.set_flag}"

        return errors

    def _tick_size_error(self: AccountSet) -> Optional[str]:
        if self.tick_size is None:
            return None
        if self.tick_size > _MAX_TICK_SIZE:
            return f"`tick_size` is above {_MAX_TICK_SIZE}."
        if self.tick_size < _MIN_TICK_SIZE and self.tick_size != _DISABLE_TICK_SIZE:
            return f"`tick_size` is below {_MIN_TICK_SIZE}."
        return None

    def _transfer_rate_error(self: AccountSet) -> Optional[str]:
        if self.transfer_rate is None:
            return None
        if self.transfer_rate > _MAX_TRANSFER_RATE:
            return f"`transfer_rate` is above {_MAX_TRANSFER_RATE}."
        if (
            self.transfer_rate < _MIN_TRANSFER_RATE
            and self.transfer_rate != _SPECIAL_CASE_TRANFER_RATE
        ):
            return f"`transfer_rate` is below {_MIN_TRANSFER_RATE}."
        return None
