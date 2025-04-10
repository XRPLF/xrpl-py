from __future__ import annotations
import json
from enum import Enum
from dataclasses import dataclass
from typing_extensions import Self


class AccountSetAsfFlag(int, Enum):
    """
    Enum for AccountSet Flags.
    """

    """
    allowed enum values
    """
    asfAccountTxnID = 5
    asfAllowTrustLineClawback = 16
    asfAuthorizedNFTokenMinter = 10
    asfDefaultRipple = 8
    asfDepositAuth = 9
    asfDisableMaster = 4
    asfDisallowIncomingCheck = 13
    asfDisallowIncomingNFTokenOffer = 12
    asfDisallowIncomingPayChan = 14
    asfDisallowIncomingTrustline = 15
    asfDisallowXRP = 3
    asfGlobalFreeze = 7
    asfNoFreeze = 6
    asfRequireAuth = 2
    asfRequireDest = 1

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of AccountSetAsfFlag from a JSON string"""
        return cls(json.loads(json_str))


