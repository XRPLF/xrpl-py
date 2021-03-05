"""
The submit_multisigned command applies a multi-signed transaction and sends it to the
network to be included in future ledgers. (You can also submit multi-signed
transactions in binary form using the submit command in submit-only mode.)

This command requires the MultiSign amendment to be enabled.

`See submit_multisigned <https://xrpl.org/submit_multisigned.html>`_
"""

from __future__ import annotations

from dataclasses import dataclass, field

from xrpl.models.base_model import REQUIRED
from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.transactions import Transaction


@dataclass(frozen=True)
class SubmitMultisigned(Request):
    """
    The submit_multisigned command applies a multi-signed transaction and sends it to
    the network to be included in future ledgers. (You can also submit multi-signed
    transactions in binary form using the submit command in submit-only mode.)

    This command requires the MultiSign amendment to be enabled.

    `See submit_multisigned <https://xrpl.org/submit_multisigned.html>`_
    """

    method: RequestMethod = field(
        default_factory=lambda: RequestMethod.SUBMIT_MULTISIGNED, init=False
    )
    tx_json: Transaction = REQUIRED
    fail_hard: bool = False
