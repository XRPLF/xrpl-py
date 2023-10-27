"""Models for the Metadata Object `NFTokenOffer`"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Union

from xrpl.models.ledger_objects import NFToken
from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class NFTokenOffer(LedgerObject):
    """
    The model for the `NFTokenOffer` Ledger Object when
    represented in a transaction's metadata.
    """

    amount: Optional[Union[str, NFToken]] = None
    flags: Optional[int] = None
    nftoken_id: Optional[str] = None
    owner: Optional[str] = None
    previous_txn_id: Optional[str] = None
    previous_txn_lgr_seq: Optional[int] = None
    destination: Optional[str] = None
    expiration: Optional[int] = None
    owner_node: Optional[str] = None
    nftoken_offer_node: Optional[str] = None
