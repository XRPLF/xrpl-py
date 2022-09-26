"""Models for the Ledger Object `NegativeUNL`"""

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
class NegativeUNL(LedgerObject):
    """The model for the `NegativeUNL` Ledger Object"""

    flags: int = REQUIRED  # type: ignore
    disabled_validators: Optional[List[DisabledValidator]] = None
    validator_to_disable: Optional[str] = None
    validator_to_enable: Optional[str] = None
    ledger_entry_type: LedgerEntryType = field(
        default=LedgerEntryType.NEGATIVE_UNL, init=False
    )


@require_kwargs_on_init
@dataclass(frozen=True)
class MDNegativeUNLFields(LedgerObject):
    """
    The model for the `NegativeUNL` Ledger Object when
    represented in a transaction's metadata.
    """

    flags: Optional[int] = None
    disabled_validators: Optional[List[DisabledValidator]] = None
    validator_to_disable: Optional[str] = None
    validator_to_enable: Optional[str] = None


@require_kwargs_on_init
@dataclass(frozen=True)
class DisabledValidator(NestedModel):
    """A model for the `DisabledValidator` object"""

    first_ledger_sequence: int = REQUIRED  # type: ignore
    public_key: str = REQUIRED  # type: ignore
