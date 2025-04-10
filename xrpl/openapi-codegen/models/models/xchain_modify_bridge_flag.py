from __future__ import annotations
import json
from enum import Enum
from dataclasses import dataclass
from typing_extensions import Self


class XChainModifyBridgeFlag(int, Enum):
    """
    Flags for the XChainModifyBridge transaction.
    """

    """
    allowed enum values
    """
    tfClearAccountCreateAmount = 65536

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of XChainModifyBridgeFlag from a JSON string"""
        return cls(json.loads(json_str))


