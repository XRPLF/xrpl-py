"""
An account in the XRP Ledger represents a holder of XRP and a sender of transactions.

See https://xrpl.org/accounts.html.

These request objects represent network client interactions that query account-level
information.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.transaction import Transaction


@dataclass(frozen=True)
class SignRequest(Request):
    """TODO: docstring"""

    method: RequestMethod = field(
        default_factory=lambda: RequestMethod.SIGN, init=False
    )
    transaction: Transaction
    secret: Optional[str] = None
    seed: Optional[str] = None
    seed_hex: Optional[str] = None
    passphrase: Optional[str] = None
    key_type: Optional[str] = None
    offline: bool = False
    build_path: Optional[bool] = None
    fee_mult_max: int = 10
    fee_div_max = 1

    def to_dict(self: SignRequest) -> Dict[str, Any]:
        """
        Returns the dictionary representation of a SignRequest.

        Returns:
            The dictionary representation of a SignRequest.
        """
        return_dict = super().to_dict()
        del return_dict["transaction"]
        return_dict["tx_json"] = self.transaction.to_dict()
        return return_dict

    def _get_errors(self: SignRequest) -> Dict[str, str]:
        """TODO: docstring"""
        errors = super()._get_errors()
        if self.secret is not None and (
            self.key_type is not None
            or self.seed is not None
            or self.seed_hex is not None
            or self.passphrase is not None
        ):
            errors["SignRequest"] = (
                "`secret` cannot be used with `key_type`, `seed`, `seed_hex`, or "
                "`passphrase`."
            )
        elif self.seed is not None and (
            self.seed is not None
            or self.seed_hex is not None
            or self.passphrase is not None
        ):
            errors[
                "SignRequest"
            ] = "`seed` cannot be used with `seed_hex`, or `passphrase`."
        elif self.seed_hex is not None and self.passphrase is not None:
            errors["SignRequest"] = "`seed` cannot be used with `passphrase`."
        elif self.key_type is None and (
            self.seed is not None
            or self.seed_hex is not None
            or self.passphrase is not None
        ):
            self.key_type = "secp256k1"  # default
        return errors
