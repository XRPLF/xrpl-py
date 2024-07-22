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

    disabled_validators: Optional[List[DisabledValidator]] = None
    """
    A list of `DisabledValidator` objects (see below), each representing a trusted
    validator that is currently disabled.
    """

    validator_to_disable: Optional[str] = None
    """
    The public key of a trusted validator that is scheduled to be disabled in the next
    flag ledger.
    """

    validator_to_re_enable: Optional[str] = None
    """
    The public key of a trusted validator in the Negative UNL that is scheduled to be
    re-enabled in the next flag ledger.
    """

    ledger_entry_type: LedgerEntryType = field(
        default=LedgerEntryType.NEGATIVE_UNL, init=False
    )


@require_kwargs_on_init
@dataclass(frozen=True)
class DisabledValidator(NestedModel):
    """A model for the `DisabledValidator` object"""

    first_ledger_sequence: int = REQUIRED  # type: ignore
    """
    The ledger index when the validator was added to the Negative UNL.
    This field is required.
    """

    public_key: str = REQUIRED  # type: ignore
    """
    The master public key of the validator, in hexadecimal.
    This field is required.
    """
