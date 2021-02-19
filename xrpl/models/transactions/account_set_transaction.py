"""
Represents an AccountSet transaction on the XRP Ledger.

An AccountSet transaction modifies the properties of an account in the XRP Ledger.

`See AccountSet <https://xrpl.org/accountset.html>`_
"""
from __future__ import annotations  # Requires Python 3.7+

from typing import Any, List, Optional

from xrpl.models.exceptions import XRPLModelValidationException
from xrpl.models.transactions.transaction import Transaction, TransactionType

_MAX_TRANSFER_RATE = 2000000000
_MIN_TRANSFER_RATE = 1000000000
_SPECIAL_CASE_TRANFER_RATE = 0

_MIN_TICK_SIZE = 3
_MAX_TICK_SIZE = 15
_DISABLE_TICK_SIZE = 0


def _validate_transfer_rate(transfer_rate: Optional[int]) -> None:
    if transfer_rate is None:
        return
    if transfer_rate > _MAX_TRANSFER_RATE:
        raise XRPLModelValidationException(
            (
                "AccountSetTransaction field `transfer_rate` is above "
                f"{_MAX_TRANSFER_RATE}."
            )
        )
    if (
        transfer_rate < _MIN_TRANSFER_RATE
        and transfer_rate != _SPECIAL_CASE_TRANFER_RATE
    ):
        raise XRPLModelValidationException(
            (
                "AccountSetTransaction field `transfer_rate` is below "
                f"{_MIN_TRANSFER_RATE}."
            )
        )


def _validate_tick_size(tick_size: Optional[int]) -> None:
    if tick_size is None:
        return
    if tick_size > _MAX_TICK_SIZE:
        raise XRPLModelValidationException(
            f"AccountSetTransaction field `tick_size` is above {_MAX_TICK_SIZE}."
        )
    if tick_size < _MIN_TICK_SIZE and tick_size != _DISABLE_TICK_SIZE:
        raise XRPLModelValidationException(
            f"AccountSetTransaction field `tick_size` is below {_MIN_TICK_SIZE}."
        )


class AccountSetTransaction(Transaction):
    """
    Represents an AccountSet transaction on the XRP Ledger.

    An AccountSet transaction modifies the properties of an account in the XRP Ledger.

    `See AccountSet <https://xrpl.org/accountset.html>`_
    """

    def __init__(
        self: AccountSetTransaction,
        *,  # forces remaining params to be named, not just listed
        account: str,
        fee: str,
        sequence: int,
        clear_flag: Optional[int] = None,
        domain: Optional[str] = None,
        email_hash: Optional[str] = None,
        message_key: Optional[str] = None,
        set_flag: Optional[int] = None,
        transfer_rate: Optional[int] = None,
        tick_size: Optional[int] = None,
        account_transaction_id: Optional[str] = None,
        flags: Optional[int] = None,
        last_ledger_sequence: Optional[int] = None,
        memos: Optional[List[Any]] = None,
        signers: Optional[List[Any]] = None,
        source_tag: Optional[int] = None,
        signing_public_key: Optional[str] = None,
        transaction_signature: Optional[str] = None,
    ) -> None:
        """Construct an AccountSetTransaction from the given parameters."""
        if domain is not None and domain.lower() != domain:
            raise XRPLModelValidationException(
                "AccountSetTransaction field `domain` is not lowercase."
            )
        if clear_flag is not None and set_flag is not None and clear_flag == set_flag:
            raise XRPLModelValidationException(
                "AccountSetTransaction fields `clear_flag` and `set_flag` are equal."
            )
        _validate_transfer_rate(transfer_rate)
        _validate_tick_size(tick_size)

        self.clear_flag = clear_flag
        self.domain = domain
        self.email_hash = email_hash
        self.message_key = message_key
        self.set_flag = set_flag
        self.transfer_rate = transfer_rate
        self.tick_size = tick_size

        super().__init__(
            account=account,
            transaction_type=TransactionType.AccountSet,
            fee=fee,
            sequence=sequence,
            account_transaction_id=account_transaction_id,
            flags=flags,
            last_ledger_sequence=last_ledger_sequence,
            memos=memos,
            signers=signers,
            source_tag=source_tag,
            signing_public_key=signing_public_key,
            transaction_signature=transaction_signature,
        )
