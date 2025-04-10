from __future__ import annotations
import json
from enum import Enum
from dataclasses import dataclass
from typing_extensions import Self


class NFTokenMintFlag(int, Enum):
    """
    Enum for NFTokenMint Transaction Flags.
    """

    """
    allowed enum values
    """
    tfBurnable = 1
    tfOnlyXRP = 2
    tfTrustLine = 4
    tfTransferable = 8

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of NFTokenMintFlag from a JSON string"""
        return cls(json.loads(json_str))
