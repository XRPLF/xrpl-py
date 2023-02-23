"""
The fee command reports the current state of the open-ledger requirements
for the transaction cost. This requires the FeeEscalation amendment to be
enabled.

This is a public command available to unprivileged users.
"""
from dataclasses import dataclass, field
from typing import Optional

from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class Fee(Request):
    """
    The fee command reports the current state of the open-ledger requirements
    for the transaction cost. This requires the FeeEscalation amendment to be
    enabled.

    This is a public command available to unprivileged users.
    """

    tx_blob: Optional[str] = None

    method: RequestMethod = field(default=RequestMethod.FEE, init=False)
