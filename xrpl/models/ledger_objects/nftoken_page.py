"""Models for the Ledger Object `NFTokenPage`"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from xrpl.models.ledger_objects.ledger_entry_type import LedgerEntryType
from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.ledger_objects.nftoken_offer import NFToken
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class NFTokenPage(LedgerObject):
    """The model for the `NFTokenPage` Ledger Object"""

    next_page_min: Optional[str] = None
    """
    The locator of the next page, if any. Details about this field and how it should be
    used are outlined below.
    """

    previous_page_min: Optional[str] = None
    """
    The locator of the previous page, if any. Details about this field and how it
    should be used are outlined below.
    """

    nftokens: List[NFToken] = REQUIRED  # type: ignore
    """
    The collection of NFToken objects contained in this NFTokenPage object. This
    specification places an upper bound of 32 NFToken objects per page. Objects are
    sorted from low to high with the NFTokenID used as the sorting parameter.
    """

    previous_txn_id: str = REQUIRED  # type: ignore
    """
    Identifies the transaction ID of the transaction that most recently modified this
    NFTokenPage object.
    """

    previous_txn_lgr_seq: int = REQUIRED  # type: ignore
    """
    The sequence of the ledger that contains the transaction that most recently
    modified this NFTokenPage object.
    """

    flags: int = 0
    """
    A bit-map of boolean flags. Flags is always 0 since there are no flags defined for
    NFTokenPage entries.
    """

    ledger_entry_type: LedgerEntryType = field(
        default=LedgerEntryType.NFTOKEN_PAGE,
        init=False,
    )
