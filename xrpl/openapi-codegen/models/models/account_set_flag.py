from __future__ import annotations
import json
from enum import Enum
from dataclasses import dataclass
from typing_extensions import Self


class AccountSetFlag(int, Enum):
    """
    Enum for AccountSet Transaction Flags.
    """

    """
    allowed enum values
    """
    tfRequireDestTag = 65536
    tfOptionalDestTag = 131072
    tfRequireAuth = 262144
    tfOptionalAuth = 524288
    tfDisallowXRP = 1048576
    tfAllowXRP = 2097152

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of AccountSetFlag from a JSON string"""
        return cls(json.loads(json_str))
