"""
The tx method retrieves information on a single transaction.

`See tx <https://xrpl.org/tx.html>`_
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from xrpl.models.base_model import REQUIRED
from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class Tx(Request):
    """
    The tx method retrieves information on a single transaction.

    `See tx <https://xrpl.org/tx.html>`_
    """

    method: RequestMethod = field(default_factory=lambda: RequestMethod.TX, init=False)
    transaction: str = REQUIRED
    binary: bool = False
    min_ledger: Optional[int] = None
    max_ledger: Optional[int] = None
