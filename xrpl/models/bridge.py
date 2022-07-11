"""A Bridge represents a cross-chain bridge."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from typing_extensions import Literal

from xrpl.models.base_model import BaseModel
from xrpl.models.currencies import IssuedCurrency
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class Bridge(BaseModel):
    """A Bridge represents a cross-chain bridge."""

    src_chain_door: str
    src_chain_issue: Union[Literal["XRP"], IssuedCurrency]
    dst_chain_door: str
    dst_chain_issue: Union[Literal["XRP"], IssuedCurrency]
