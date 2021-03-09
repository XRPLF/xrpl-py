"""
The submit_multisigned command applies a multi-signed transaction and sends it to the
network to be included in future ledgers. (You can also submit multi-signed
transactions in binary form using the submit command in submit-only mode.)

This command requires the MultiSign amendment to be enabled.

`See submit_multisigned <https://xrpl.org/submit_multisigned.html>`_
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from xrpl.models.base_model import REQUIRED
from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.transactions import Transaction
from xrpl.models.utils import field, require_kwargs_on_init


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

    method: RequestMethod = field(
        default_factory=lambda: RequestMethod.SUBMIT_MULTISIGNED, init=False
    )
    transaction: Transaction = REQUIRED
    fail_hard: bool = False

    def to_dict(self: SubmitMultisigned) -> Dict[str, Any]:
        """
        Returns the dictionary representation of a SubmitMultisigned.

        Returns:
            The dictionary representation of a SubmitMultisigned.
        """
        return_dict = super().to_dict()
        del return_dict["transaction"]
        return_dict["tx_json"] = self.transaction.to_dict()
        return return_dict
