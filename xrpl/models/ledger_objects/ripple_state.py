"""Models for the Ledger Object `RippleState`"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from xrpl.models.amounts.issued_currency_amount import IssuedCurrencyAmount
from xrpl.models.ledger_objects.ledger_entry_type import LedgerEntryType
from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class RippleState(LedgerObject):
    """The model for the `RippleState` Ledger Object"""

    balance: IssuedCurrencyAmount = REQUIRED  # type: ignore
    """
    The balance of the trust line, from the perspective of the low account. A negative
    balance indicates that the high account holds tokens issued by the low account. The
    issuer in this is always set to the neutral value ACCOUNT_ONE. This field is
    required.
    """

    high_limit: IssuedCurrencyAmount = REQUIRED  # type: ignore
    """
    The limit that the high account has set on the trust line. The `issuer` is the
    address of the high account that set this limit. This field is required.
    """

    low_limit: IssuedCurrencyAmount = REQUIRED  # type: ignore
    """
    The limit that the low account has set on the trust line. The `issuer` is the
    address of the low account that set this limit. This field is required.
    """

    previous_txn_id: str = REQUIRED  # type: ignore
    """
    The identifying hash of the transaction that most recently modified this entry.
    This field is required.
    """

    previous_txn_lgr_seq: int = REQUIRED  # type: ignore
    """
    The index of the ledger that contains the transaction that most recently modified
    this entry. This field is required.
    """

    high_node: Optional[str] = None
    """
    (Omitted in some historical ledgers) A hint indicating which page of the high
    account's owner directory links to this entry, in case the directory consists of
    multiple pages.
    """

    high_quality_in: Optional[int] = None
    """
    The inbound quality set by the high account, as an integer in the implied ratio
    `HighQualityIn`:1,000,000,000. As a special case, the value 0 is equivalent to 1
    billion, or face value.
    """

    high_quality_out: Optional[int] = None
    """
    The outbound quality set by the high account, as an integer in the implied ratio
    `HighQualityOut`:1,000,000,000. As a special case, the value 0 is equivalent to 1
    billion, or face value.
    """

    low_node: Optional[str] = None
    """
    (Omitted in some historical ledgers) A hint indicating which page of the low
    account's owner directory links to this entry, in case the directory consists of
    multiple pages.
    """

    low_quality_in: Optional[int] = None
    """
    The inbound quality set by the low account, as an integer in the implied ratio
    `LowQualityIn`:1,000,000,000. As a special case, the value 0 is equivalent to 1
    billion, or face value.
    """

    low_quality_out: Optional[int] = None
    """
    The outbound quality set by the low account, as an integer in the implied ratio
    `LowQualityOut`:1,000,000,000. As a special case, the value 0 is equivalent to 1
    billion, or face value.
    """

    flags: int = REQUIRED  # type: ignore
    """
    A bit-map of boolean options enabled for this entry.
    """

    ledger_entry_type: LedgerEntryType = field(
        default=LedgerEntryType.RIPPLE_STATE,
        init=False,
    )
    """
    The value `0x0072`, mapped to the string `RippleState`, indicates that this is a
    RippleState entry.
    """


class RippleStateFlag(Enum):
    """The flags for the `RippleState` Ledger Object"""

    LSF_LOW_RESERVE = 0x00010000
    LSF_HIGH_RESERVE = 0x00020000
    LSF_LOW_AUTH = 0x00040000
    LSF_HIGH_AUTH = 0x00080000
    LSF_LOW_NO_RIPPLE = 0x00100000
    LSF_HIGH_NO_RIPPLE = 0x00200000
    LSF_LOW_FREEZE = 0x00400000
    LSF_HIGH_FREEZE = 0x00800000
