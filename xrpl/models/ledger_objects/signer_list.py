"""Models for the Ledger Object `SignerList`"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from xrpl.models.ledger_objects.ledger_entry_type import LedgerEntryType
from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.signer_list_set import SignerEntry
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class SignerList(LedgerObject):
    """The model for the `SignerList` Ledger Object"""

    flags: int = REQUIRED  # type: ignore
    owner_node: str = REQUIRED  # type: ignore
    previous_txn_id: str = REQUIRED  # type: ignore
    previous_txn_lgr_seq: int = REQUIRED  # type: ignore
    signer_entries: List[SignerEntry] = REQUIRED  # type: ignore
    signer_list_id: int = REQUIRED  # type: ignore
    signer_quorum: int = REQUIRED  # type: ignore
    ledger_entry_type: LedgerEntryType = field(
        default=LedgerEntryType.SIGNER_LIST,
        init=False,
    )


@require_kwargs_on_init
@dataclass(frozen=True)
class MDSignerListFields(LedgerObject):
    """
    The model for the `SignerList` Ledger Object when
    represented in a transaction's metadata.
    """

    flags: Optional[int] = None
    owner_node: Optional[str] = None
    previous_txn_id: Optional[str] = None
    previous_txn_lgr_seq: Optional[int] = None
    signer_entries: Optional[List[SignerEntry]] = None
    signer_list_id: Optional[int] = None
    signer_quorum: Optional[int] = None


class SignerListFlag(Enum):
    """The flags for the `SignerList` Ledger Object"""

    LSF_ONE_OWNER_COUNT = 0x00010000
