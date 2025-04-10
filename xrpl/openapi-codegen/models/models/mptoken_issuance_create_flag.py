from __future__ import annotations
import json
from enum import Enum
from dataclasses import dataclass
from typing_extensions import Self


class MPTokenIssuanceCreateFlag(int, Enum):
    """
    Enum for MPTokenIssuanceCreate Transaction Flags.
    """

    """
    allowed enum values
    """
    tfMPTCanLock = 2
    tfMPTRequireAuth = 4
    tfMPTCanEscrow = 8
    tfMPTCanTrade = 16
    tfMPTCanTransfer = 32
    tfMPTCanClawback = 64

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of MPTokenIssuanceCreateFlag from a JSON string"""
        return cls(json.loads(json_str))


