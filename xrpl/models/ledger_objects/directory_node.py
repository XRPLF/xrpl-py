"""Models for the Ledger Object `DirectoryNode`"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from xrpl.models.ledger_objects.ledger_entry_type import LedgerEntryType
from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class DirectoryNode(LedgerObject):
    """The model for the `DirectoryNode` Ledger Object"""

    exchange_rate: Optional[str] = None
    """
    (Offer Directories only) DEPRECATED. Do not use.
    """

    indexes: List[str] = REQUIRED  # type: ignore
    """
    The contents of this Directory: an array of IDs of other objects.
    This field is required.
    """

    index_next: Optional[int] = None
    """
    If this Directory consists of multiple pages, this ID links to the next object in
    the chain, wrapping around at the end.
    """

    index_previous: Optional[int] = None
    """
    If this Directory consists of multiple pages, this ID links to the previous object
    in the chain, wrapping around at the beginning. This field is required.
    """

    owner: Optional[str] = None
    """
    (Owner Directories only) The address of the account that owns the objects in this
    directory.
    """

    root_index: str = REQUIRED  # type: ignore
    """
    The ID of root object for this directory. This field is required.
    """

    taker_gets_currency: Optional[str] = None
    """
    (Offer Directories only) The currency code of the `TakerGets` amount from the offers
    in this directory.
    """

    taker_gets_issuer: Optional[str] = None
    """
    (Offer Directories only) The issuer of the `TakerGets` amount from the offers in
    this directory.
    """

    taker_pays_currency: Optional[str] = None
    """
    (Offer Directories only) The currency code of the `TakerPays` amount from the offers
    in this directory.
    """

    taker_pays_issuer: Optional[str] = None
    """
    (Offer Directories only) The issuer of the `TakerPays` amount from the offers in
    this directory.
    """

    nftoken_id: Optional[str] = None
    """
    (Non-Fungible Token Directories only) The ID of the non-fungible token.
    """

    flags: int = 0
    """
    A bit-map of boolean flags. Flags is always 0 since there are no flags defined for
    DirectoryNode entries.
    """

    ledger_entry_type: LedgerEntryType = field(
        default=LedgerEntryType.DIRECTORY_NODE,
        init=False,
    )
