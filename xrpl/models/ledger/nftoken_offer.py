"""Models for the Ledger Object `NFTokenOffer`"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union

from xrpl.models.base_model import BaseModel
from xrpl.models.ledger.ledger_entry_type import LedgerEntryType
from xrpl.models.ledger.ledger_object import LedgerObject
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class NFTokenOffer(LedgerObject):
    """The model for the `NFTokenOffer` Ledger Object"""

    amount: Union[str, NFToken] = REQUIRED  # type: ignore
    flags: int = REQUIRED  # type: ignore
    nftoken_id: str = REQUIRED  # type: ignore
    owner: str = REQUIRED  # type: ignore
    previous_txn_id: str = REQUIRED  # type: ignore
    previous_txn_lgr_seq: int = REQUIRED  # type: ignore
    destination: Optional[str] = None
    expiration: Optional[int] = None
    owner_node: Optional[str] = None
    nftoken_offer_node: Optional[str] = None
    ledger_entry_type: LedgerEntryType = field(
        default=LedgerEntryType.NFTOKEN_OFFER,
        init=False,
    )


@require_kwargs_on_init
@dataclass(frozen=True)
class NFToken(BaseModel):  #
    """A model for the `NFToken` object"""

    nftoken_id: str = REQUIRED  # type: ignore
    uri: str = REQUIRED  # type: ignore


class NFTokenOfferFlags(Enum):
    """The flags for the `NFTokenOffer` Ledger Object"""

    LSF_SELL_NFTOKEN = 0x00000001
