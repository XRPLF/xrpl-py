from __future__ import annotations
import json
from enum import Enum
from dataclasses import dataclass
from typing_extensions import Self


class PaymentChannelClaimFlag(int, Enum):
    """
    Enum for PaymentChannelClaim Transaction Flags.
    """

    """
    allowed enum values
    """
    tfRenew = 65536
    tfClose = 131072

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of PaymentChannelClaimFlag from a JSON string"""
        return cls(json.loads(json_str))
