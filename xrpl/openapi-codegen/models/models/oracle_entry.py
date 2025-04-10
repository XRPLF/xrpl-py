"""Model for OracleEntry."""

from dataclasses import dataclass
from typing import Optional
from xrpl.models.base_model import BaseModel
from xrpl.models.oracle_entry_oracle import OracleEntryOracle
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class OracleEntry(BaseModel):
    """
    Retrieve an Oracle entry, which represents a single price oracle that can store token
    prices.
    """

    oracle: Optional[OracleEntryOracle] = None
