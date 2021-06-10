"""
The tx method retrieves information on a single transaction.

`See tx <https://xrpl.org/tx.html>`_
"""

from dataclasses import dataclass, field
from typing import Optional

from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class Tx(Request):
    """
    The tx method retrieves information on a single transaction.

    `See tx <https://xrpl.org/tx.html>`_
    """

    method: RequestMethod = field(default=RequestMethod.TX, init=False)
    transaction: str = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """

    binary: bool = False
    min_ledger: Optional[int] = None
    max_ledger: Optional[int] = None
