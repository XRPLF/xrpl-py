"""Models for the Metadata Object `NegativeUNL`"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from xrpl.models.ledger_objects import DisabledValidator
from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class NegativeUNL(LedgerObject):
    """
    The model for the `NegativeUNL` Ledger Object when
    represented in a transaction's metadata.
    """

    flags: Optional[int] = None
    disabled_validators: Optional[List[DisabledValidator]] = None
    validator_to_disable: Optional[str] = None
    validator_to_enable: Optional[str] = None
