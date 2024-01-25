"""Models for the Ledger Object `LedgerHashes`"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from xrpl.models.ledger_objects.ledger_entry_type import LedgerEntryType
from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class LedgerHashes(LedgerObject):
    """The model for the `LedgerHashes` Ledger Object"""

    first_ledger_sequence: Optional[int] = None
    """
    DEPRECATED Do not use. (The "recent hashes" object on Mainnet has the value 2 in
    this field as a result of an old software bug. That value gets carried forward as
    the "recent hashes" object is updated. New "previous history" objects do not have
    this field, nor do "recent hashes" objects in parallel networks started with more
    recent versions of rippled.)
    """

    last_ledger_sequence: Optional[int] = None
    """
    The Ledger Index of the last entry in this object's `Hashes` array.
    """

    hashes: List[str] = REQUIRED  # type: ignore
    """
    An array of up to 256 ledger hashes. The contents depend on which sub-type of
    LedgerHashes object this is. This field is required.
    """

    flags: int = REQUIRED  # type: ignore
    """
    A bit-map of boolean flags. Flags is always 0 since there are no flags defined for
    Escrow entries. This field is required.
    """

    ledger_entry_type: LedgerEntryType = field(
        default=LedgerEntryType.LEDGER_HASHES,
        init=False,
    )
    """
    The value `0x0068`, mapped to the string `LedgerHashes`, indicates that this object
    is a list of ledger hashes.
    """
