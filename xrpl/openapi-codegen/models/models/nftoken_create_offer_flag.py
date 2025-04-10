from __future__ import annotations
import json
from enum import Enum
from dataclasses import dataclass
from typing_extensions import Self


class NFTokenCreateOfferFlag(int, Enum):
    """
    Enum for NFTokenCreateOffer Transaction Flags.
    """

    """
    allowed enum values
    """
    tfSellNFToken = 1

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of NFTokenCreateOfferFlag from a JSON string"""
        return cls(json.loads(json_str))


