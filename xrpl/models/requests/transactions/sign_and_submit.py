"""
The submit method applies a transaction and sends it to the network to be confirmed and
included in future ledgers.

This command has two modes:
* Submit-only mode takes a signed, serialized transaction as a binary blob, and submits
it to the network as-is. Since signed transaction objects are immutable, no part of the
transaction can be modified or automatically filled in after submission.
* Sign-and-submit mode takes a JSON-formatted Transaction object, completes and signs
the transaction in the same manner as the sign method, and then submits the signed
transaction. We recommend only using this mode for testing and development.

To send a transaction as robustly as possible, you should construct and sign it in
advance, persist it somewhere that you can access even after a power outage, then
submit it as a tx_blob. After submission, monitor the network with the tx method
command to see if the transaction was successfully applied; if a restart or other
problem occurs, you can safely re-submit the tx_blob transaction: it won't be applied
twice since it has the same sequence number as the old transaction.

`See submit <https://xrpl.org/submit.html>`_
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from xrpl.models.transactions.submit import Submit
from xrpl.models.transactions.transaction import REQUIRED, Transaction


@dataclass(frozen=True)
class SignAndSubmit(Submit):
    """
    The submit method applies a transaction and sends it to the network to be confirmed
    and included in future ledgers.

    This command has two modes:
    * Submit-only mode takes a signed, serialized transaction as a binary blob, and
    submits it to the network as-is. Since signed transaction objects are immutable, no
    part of the transaction can be modified or automatically filled in after submission.
    * Sign-and-submit mode takes a JSON-formatted Transaction object, completes and
    signs the transaction in the same manner as the sign method, and then submits the
    signed transaction. We recommend only using this mode for testing and development.

    To send a transaction as robustly as possible, you should construct and sign it in
    advance, persist it somewhere that you can access even after a power outage, then
    submit it as a tx_blob. After submission, monitor the network with the tx method
    command to see if the transaction was successfully applied; if a restart or other
    problem occurs, you can safely re-submit the tx_blob transaction: it won't be
    applied twice since it has the same sequence number as the old transaction.

    `See submit <https://xrpl.org/submit.html>`_
    """

    transaction: Transaction = REQUIRED
    secret: Optional[str] = None
    seed: Optional[str] = None
    seed_hex: Optional[str] = None
    passphrase: Optional[str] = None
    key_type: Optional[str] = None
    offline: bool = False
    build_path: Optional[bool] = None
    fee_mult_max: int = 10
    fee_div_max: int = 1

    def to_dict(self: SignAndSubmit) -> Dict[str, Any]:
        """
        Returns the dictionary representation of a SignAndSubmit.

        Returns:
            The dictionary representation of a SignAndSubmit.
        """
        return_dict = super().to_dict()
        del return_dict["transaction"]
        return_dict["tx_json"] = self.transaction.to_dict()
        return return_dict

    def _get_errors(self: SignAndSubmit) -> Dict[str, str]:
        errors = super()._get_errors()
        if self.secret is not None and (
            self.key_type is not None
            or self.seed is not None
            or self.seed_hex is not None
            or self.passphrase is not None
        ):
            errors["SignAndSubmit"] = (
                "`secret` cannot be used with `key_type`, `seed`, `seed_hex`, or "
                "`passphrase`."
            )
        elif self.seed is not None and (
            self.seed_hex is not None or self.passphrase is not None
        ):
            errors[
                "SignAndSubmit"
            ] = "`seed` cannot be used with `seed_hex` or `passphrase`."
        elif self.seed_hex is not None and self.passphrase is not None:
            errors["SignAndSubmit"] = "`seed` cannot be used with `passphrase`."
        elif self.key_type is None and (
            self.seed is not None
            or self.seed_hex is not None
            or self.passphrase is not None
        ):
            self.key_type = "secp256k1"  # default
        return errors
