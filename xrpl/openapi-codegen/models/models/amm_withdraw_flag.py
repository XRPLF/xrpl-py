from __future__ import annotations
import json
from enum import Enum
from dataclasses import dataclass
from typing_extensions import Self


class AMMWithdrawFlag(int, Enum):
    """
    Enum for AMMWithdraw Transaction Flags.
    """

    """
    allowed enum values
    """
    tfLPToken = 65536
    tfWithdrawAll = 131072
    tfOneAssetWithdrawAll = 262144
    tfSingleAsset = 524288
    tfTwoAsset = 1048576
    tfOneAssetLPToken = 2097152
    tfLimitLPToken = 4194304

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of AMMWithdrawFlag from a JSON string"""
        return cls(json.loads(json_str))
