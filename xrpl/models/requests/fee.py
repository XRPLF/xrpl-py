"""
The fee command reports the current state of the open-ledger requirements
for the transaction cost. This requires the FeeEscalation amendment to be
enabled.

This is a public command available to unprivileged users.
"""
from dataclasses import dataclass

from xrpl.models.requests.request import Request, RequestMethod


@dataclass(frozen=True)
class Fee(Request):
    """
    The fee command reports the current state of the open-ledger requirements
    for the transaction cost. This requires the FeeEscalation amendment to be
    enabled.

    This is a public command available to unprivileged users.
    """

    method: RequestMethod = RequestMethod.FEE
