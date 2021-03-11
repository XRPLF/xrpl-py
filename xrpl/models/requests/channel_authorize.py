"""
The channel_authorize method creates a signature that can
be used to redeem a specific amount of XRP from a payment channel.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from xrpl.models.base_model import REQUIRED
from xrpl.models.requests.request import Request, RequestMethod


@dataclass(frozen=True)
class ChannelAuthorize(Request):
    """
    The channel_authorize method creates a signature that can
    be used to redeem a specific amount of XRP from a payment channel.
    """

    method: RequestMethod = RequestMethod.CHANNEL_AUTHORIZE
    channel_id: str = REQUIRED  # type: ignore
    amount: str = REQUIRED  # type: ignore
    secret: Optional[str] = None
    seed: Optional[str] = None
    seed_hex: Optional[str] = None
    passphrase: Optional[str] = None
    key_type: Optional[str] = None

    def _get_errors(self: ChannelAuthorize) -> Dict[str, str]:
        errors = super()._get_errors()
        signing_methods = [
            method
            for method in [
                self.secret,
                self.seed,
                self.seed_hex,
                self.passphrase,
            ]
            if method is not None
        ]
        if len(signing_methods) != 1:
            errors[
                "ChannelAuthorize"
            ] = "Must set exactly one of `secret`, `seed, `seed_hex`, or `passphrase`"
        return errors
