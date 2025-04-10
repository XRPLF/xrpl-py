from __future__ import annotations
import json
from enum import Enum
from dataclasses import dataclass
from typing_extensions import Self


class AMMDepositFlag(int, Enum):
    """
    Enum for AMMDeposit Transaction Flags.
    """

    """
    allowed enum values
    """
    tfLPToken = 65536
    tfTwoAsset = 1048576
    tfTwoAssetIfEmpty = 8388608
    tfSingleAsset = 524288
    tfOneAssetLPToken = 2097152
    tfLimitLPToken = 4194304

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of AMMDepositFlag from a JSON string"""
        return cls(json.loads(json_str))
