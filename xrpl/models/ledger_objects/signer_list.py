"""Models for the Ledger Object `SignerList`"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List

from xrpl.models.ledger_objects.ledger_entry_type import LedgerEntryType
from xrpl.models.ledger_objects.ledger_object import HasPreviousTxnID, LedgerObject
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.signer_list_set import SignerEntry
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class SignerList(LedgerObject, HasPreviousTxnID):
    """The model for the `SignerList` Ledger Object"""

    owner_node: str = REQUIRED  # type: ignore
    """
    A hint indicating which page of the owner directory links to this object, in case
    the directory consists of multiple pages. This field is required.
    """

    signer_entries: List[SignerEntry] = REQUIRED  # type: ignore
    """
    An array of Signer Entry objects representing the parties who are part of this
    signer list. This field is required.
    """

    signer_list_id: int = REQUIRED  # type: ignore
    """
    An ID for this signer list. Currently always set to 0. If a future amendment allows
    multiple signer lists for an account, this may change. This field is required.
    """

    signer_quorum: int = REQUIRED  # type: ignore
    """
    A target number for signer weights. To produce a valid signature for the owner of
    this SignerList, the signers must provide valid signatures whose weights sum to
    this value or more. This field is required.
    """

    ledger_entry_type: LedgerEntryType = field(
        default=LedgerEntryType.SIGNER_LIST,
        init=False,
    )


class SignerListFlag(Enum):
    """The flags for the `SignerList` Ledger Object"""

    LSF_ONE_OWNER_COUNT = 0x00010000
