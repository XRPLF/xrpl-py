from __future__ import annotations
import json
from enum import Enum
from dataclasses import dataclass
from typing_extensions import Self


class PaymentFlag(int, Enum):
    """
    Enum for Payment Transaction Flags.
    """

    """
    allowed enum values
    """
    tfNoRippleDirect = 65536
    tfPartialPayment = 131072
    tfLimitQuality = 262144

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of PaymentFlag from a JSON string"""
        return cls(json.loads(json_str))
