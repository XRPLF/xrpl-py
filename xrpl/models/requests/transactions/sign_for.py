"""
The sign_for command provides one signature for a multi-signed transaction.

By default, this method is admin-only. It can be used as a public method if the server
has enabled public signing.

This command requires the MultiSign amendment to be enabled.

`See sign_for <https://xrpl.org/sign_for.html>`_
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.transactions.transaction import REQUIRED, Transaction


@dataclass(frozen=True)
class SignFor(Request):
    """
    The sign_for command provides one signature for a multi-signed transaction.

    By default, this method is admin-only. It can be used as a public method if the
    server has enabled public signing.

    This command requires the MultiSign amendment to be enabled.

    `See sign_for <https://xrpl.org/sign_for.html>`_
    """

    method: RequestMethod = field(default=RequestMethod.SIGN_FOR, init=False)
    account: str = REQUIRED
    transaction: Transaction = REQUIRED
    secret: Optional[str] = None
    seed: Optional[str] = None
    seed_hex: Optional[str] = None
    passphrase: Optional[str] = None
    key_type: Optional[str] = None

    def to_dict(self: SignFor) -> Dict[str, Any]:
        """
        Returns the dictionary representation of a SignFor.

        Returns:
            The dictionary representation of a SignFor.
        """
        return_dict = super().to_dict()
        del return_dict["transaction"]
        return_dict["tx_json"] = self.transaction.to_dict()
        return return_dict

    def _get_errors(self: SignFor) -> Dict[str, str]:
        errors = super()._get_errors()
        if not self._has_only_one_seed():
            errors[
                "Sign"
            ] = "Must have only one of `secret`, `seed`, `seed_hex`, and `passphrase."

        if self.secret is not None and self.key_type is not None:
            errors["key_type"] = "Must omit `key_type` if `secret` is provided."

        return errors

    def _has_only_one_seed(self: SignFor) -> bool:
        items = [self.secret, self.seed, self.seed_hex, self.passphrase]
        return len([item for item in items if item is not None]) == 1
