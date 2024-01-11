"""
The tx method retrieves information on a single transaction.

`See tx <https://xrpl.org/tx.html>`_
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class Tx(Request):
    """
    The tx method retrieves information on a single transaction.
    The Request must contain either transaction or CTID parameter, but not both.

    `See tx <https://xrpl.org/tx.html>`_
    """

    method: RequestMethod = field(default=RequestMethod.TX, init=False)
    transaction: Optional[str] = None
    binary: bool = False
    min_ledger: Optional[int] = None
    max_ledger: Optional[int] = None
    ctid: Optional[str] = None

    def _get_errors(self: Tx) -> Dict[str, str]:
        errors = super()._get_errors()
        if not self._has_only_one_input():
            errors[
                "Tx"
            ] = "Must have only one of `ctid` or `transaction`, but not both."
        return errors

    def _has_only_one_input(self: Tx) -> bool:
        present_items = [
            item for item in [self.transaction, self.ctid] if item is not None
        ]
        return len(present_items) == 1
