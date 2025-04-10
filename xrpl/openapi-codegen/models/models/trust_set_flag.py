from __future__ import annotations
import json
from enum import Enum
from dataclasses import dataclass
from typing_extensions import Self


class TrustSetFlag(int, Enum):
    """
    Enum for TrustSet Transaction Flags.
    """

    """
    allowed enum values
    """
    tfSetfAuth = 65536
    tfSetNoRipple = 131072
    tfClearNoRipple = 262144
    tfSetFreeze = 1048576
    tfClearFreeze = 2097152

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of TrustSetFlag from a JSON string"""
        return cls(json.loads(json_str))


