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

    method: RequestMethod = field(
        default_factory=lambda: RequestMethod.SIGN_FOR, init=False
    )
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
        if self.secret is not None and (
            self.key_type is not None
            or self.seed is not None
            or self.seed_hex is not None
            or self.passphrase is not None
        ):
            errors["SignFor"] = (
                "`secret` cannot be used with `key_type`, `seed`, `seed_hex`, or "
                "`passphrase`."
            )
        elif self.seed is not None and (
            self.seed_hex is not None or self.passphrase is not None
        ):
            errors["SignFor"] = "`seed` cannot be used with `seed_hex` or `passphrase`."
        elif self.seed_hex is not None and self.passphrase is not None:
            errors["SignFor"] = "`seed` cannot be used with `passphrase`."
        elif self.key_type is None and (
            self.seed is not None
            or self.seed_hex is not None
            or self.passphrase is not None
        ):
            self.key_type = "secp256k1"  # default
        return errors
