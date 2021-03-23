"""Model for AccountSet transaction type."""
from __future__ import annotations  # Requires Python 3.7+

from dataclasses import dataclass, field
from typing import Dict, Optional

from typing_extensions import Final

from xrpl.models.transactions.transaction import Transaction, TransactionType
from xrpl.models.utils import require_kwargs_on_init

_MAX_TRANSFER_RATE: Final[int] = 2000000000
_MIN_TRANSFER_RATE: Final[int] = 1000000000
_SPECIAL_CASE_TRANFER_RATE: Final[int] = 0

_MIN_TICK_SIZE: Final[int] = 3
_MAX_TICK_SIZE: Final[int] = 15
_DISABLE_TICK_SIZE: Final[int] = 0


@require_kwargs_on_init
@dataclass(frozen=True)
class AccountSet(Transaction):
    """
    Represents an `AccountSet transaction <https://xrpl.org/accountset.html>`_,
    which modifies the properties of an account in the XRP Ledger.
    """

    #: Disable a specific `AccountSet Flag
    #: <https://xrpl.org/accountset.html#accountset-flags>`_
    clear_flag: Optional[int] = None

    #: Set the DNS domain of the account owner.
    domain: Optional[str] = None

    #: Set the MD5 Hash to be used for generating an avatar image for this
    #: account.
    email_hash: Optional[str] = None

    #: Set a public key for sending encrypted messages to this account.
    message_key: Optional[str] = None

    #: Enable a specific `AccountSet Flag
    #: <https://xrpl.org/accountset.html#accountset-flags>`_
    set_flag: Optional[int] = None

    #: Set the transfer fee to use for tokens issued by this account. See
    #: `TransferRate <https://xrpl.org/accountset.html#transferrate`_ for
    #: details.
    transfer_rate: Optional[int] = None

    #: Set the tick size to use when trading tokens issued by this account in
    #: the decentralized exchange. See `Tick Size
    #: <https://xrpl.org/ticksize.html>`_ for details.
    tick_size: Optional[int] = None

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
