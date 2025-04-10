from __future__ import annotations
import json
from enum import Enum
from dataclasses import dataclass
from typing_extensions import Self


class MPTokenIssuanceSetFlag(int, Enum):
    """
    Enum for MPTokenIssuanceSet Transaction Flags.
    """

    """
    allowed enum values
    """
    tfMPTLock = 1
    tfMPTUnlock = 2

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of MPTokenIssuanceSetFlag from a JSON string"""
        return cls(json.loads(json_str))


