from __future__ import annotations
import json
from enum import Enum
from dataclasses import dataclass
from typing_extensions import Self


class OfferCreateFlag(int, Enum):
    """
    Enum for OfferCreate Transaction Flags.
    """

    """
    allowed enum values
    """
    tfPassive = 65536
    tfImmediateOrCancel = 131072
    tfFillOrKill = 262144
    tfSell = 524288

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of OfferCreateFlag from a JSON string"""
        return cls(json.loads(json_str))
