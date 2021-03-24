"""
The submit_multisigned command applies a multi-signed transaction and sends it to the
network to be included in future ledgers. (You can also submit multi-signed
transactions in binary form using the submit command in submit-only mode.)

This command requires the MultiSign amendment to be enabled.

`See submit_multisigned <https://xrpl.org/submit_multisigned.html>`_
"""
from dataclasses import dataclass, field

from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class SubmitMultisigned(Request):
    """
    The submit_multisigned command applies a multi-signed transaction and sends it to
    the network to be included in future ledgers. (You can also submit multi-signed
    transactions in binary form using the submit command in submit-only mode.)

    This command requires the MultiSign amendment to be enabled.

    `See submit_multisigned <https://xrpl.org/submit_multisigned.html>`_
    """

    method: RequestMethod = field(default=RequestMethod.SUBMIT_MULTISIGNED, init=False)
    #: This field is required.
    tx_json: Transaction = REQUIRED  # type: ignore
    fail_hard: bool = False
