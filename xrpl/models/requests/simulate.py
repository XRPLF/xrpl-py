"""This request simulates a transaction without submitting it to the network."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from typing_extensions import Self

from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class Simulate(Request):
    """
    The `simulate` method simulates a transaction without submitting it to the
    network.
    """

    tx_blob: Optional[str] = None

    tx_json: Optional[Transaction] = None

    binary: Optional[bool] = None

    method: RequestMethod = field(default=RequestMethod.SIMULATE, init=False)

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()
        if (self.tx_blob is None) == (self.tx_json is None):
            errors["tx"] = "Must have exactly one of `tx_blob` and `tx_json` fields."
        return errors
