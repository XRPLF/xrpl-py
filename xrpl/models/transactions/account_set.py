"""
Represents an AccountSet transaction on the XRP Ledger.

An AccountSet transaction modifies the properties of an account in the XRP Ledger.

`See AccountSet <https://xrpl.org/accountset.html>`_
"""
from __future__ import annotations  # Requires Python 3.7+

from dataclasses import dataclass
from typing import Dict, Optional

from xrpl.models.transactions.transaction import Transaction, TransactionType

_MAX_TRANSFER_RATE = 2000000000
_MIN_TRANSFER_RATE = 1000000000
_SPECIAL_CASE_TRANFER_RATE = 0

_MIN_TICK_SIZE = 3
_MAX_TICK_SIZE = 15
_DISABLE_TICK_SIZE = 0


@dataclass(frozen=True)
class AccountSet(Transaction):
    """
    Represents an AccountSet transaction on the XRP Ledger.

    An AccountSet transaction modifies the properties of an account in the XRP Ledger.

    `See AccountSet <https://xrpl.org/accountset.html>`_
    """

    clear_flag: Optional[int] = None
    domain: Optional[str] = None
    email_hash: Optional[str] = None
    message_key: Optional[str] = None
    set_flag: Optional[int] = None
    transfer_rate: Optional[int] = None
    tick_size: Optional[int] = None
    transaction_type: TransactionType = TransactionType.AccountSet

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
                "clear_flag"
            ] = f"Clear flag {self.clear_flag} is equal to set flag {self.set_flag}"
            errors[
                "set_flag"
            ] = f"Set flag {self.set_flag} is equal to clear flag {self.clear_flag}"

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
