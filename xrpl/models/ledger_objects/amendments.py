"""Models for the Ledger Object `Amendments`"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from xrpl.models.ledger_objects.ledger_entry_type import LedgerEntryType
from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.nested_model import NestedModel
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class Amendments(LedgerObject):
    """The model for the `Amendments` Ledger Object"""

    amendments: Optional[List[str]] = None
    """
    Array of 256-bit amendment IDs for all currently enabled amendments. If omitted,
    there are no enabled amendments.
    """

    flags: int = 0
    """
    A bit-map of boolean flags. Currently, the protocol defines no flags for
    `Amendments` objects. The value is always 0.
    """

    ledger_entry_type: LedgerEntryType = field(
        default=LedgerEntryType.AMENDMENTS,
        init=False,
    )

    majorities: Optional[List[Majority]] = None
    """
    Array of objects describing the status of amendments that have majority support but
    are not yet enabled. If omitted, there are no pending amendments with majority
    support.
    """


@require_kwargs_on_init
@dataclass(frozen=True)
class Majority(NestedModel):
    """A model for the `Majority` object"""

    amendment: str = REQUIRED  # type: ignore
    close_time: int = REQUIRED  # type: ignore
