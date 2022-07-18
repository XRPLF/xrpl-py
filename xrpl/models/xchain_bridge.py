"""A XChainBridge represents a cross-chain bridge."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from typing_extensions import Literal

from xrpl.models.base_model import BaseModel
from xrpl.models.currencies import IssuedCurrency
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class XChainBridge(BaseModel):
    """A XChainBridge represents a cross-chain bridge."""

    locking_chain_door: str
    locking_chain_issue: Union[Literal["XRP"], IssuedCurrency]
    issuing_chain_door: str
    issuing_chain_issue: Union[Literal["XRP"], IssuedCurrency]
