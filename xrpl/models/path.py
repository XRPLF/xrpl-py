"""
A path is an ordered array. Each member of a path is an
object that specifies the step.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from typing_extensions import Self, TypeGuard

from xrpl.constants import HEX_MPTID_REGEX
from xrpl.models.base_model import BaseModel
from xrpl.models.utils import get_mpt_issuer


def _is_valid_mptid(candidate: object) -> TypeGuard[str]:
    return isinstance(candidate, str) and bool(HEX_MPTID_REGEX.fullmatch(candidate))


@dataclass(frozen=True, kw_only=True)
class PathStep(BaseModel):
    """A PathStep represents an individual step along a Path."""

    account: Optional[str] = None
    currency: Optional[str] = None
    issuer: Optional[str] = None
    mpt_issuance_id: Optional[str] = None
    """
    The MPT to convert to, in place of ``currency``. ``issuer`` may be omitted; if
    set, it must be the MPT's issuer. Requires the MPTokensV2 amendment.
    """
    type: Optional[int] = None
    type_hex: Optional[str] = None

    def _get_errors(self: Self) -> Dict[str, str]:
        return {
            key: value
            for key, value in {
                **super()._get_errors(),
                "account": self._get_account_error(),
                "currency": self._get_currency_error(),
                "issuer": self._get_issuer_error(),
                "mpt_issuance_id": self._get_mpt_issuance_id_error(),
            }.items()
            if value is not None
        }

    def _get_account_error(self: Self) -> Optional[str]:
        if self.account is None:
            return None
        if self.currency is not None or self.issuer is not None:
            return "Cannot set account if currency or issuer are set"
        if self.mpt_issuance_id is not None:
            return "Cannot set account if mpt_issuance_id is set"
        return None

    def _get_currency_error(self: Self) -> Optional[str]:
        if self.currency is None:
            return None
        if self.account is not None:
            return "Cannot set currency if account is set"
        if self.issuer is not None and self.currency.upper() == "XRP":
            return "Cannot set issuer if currency is XRP"
        return None

    def _get_issuer_error(self: Self) -> Optional[str]:
        if self.issuer is None:
            return None
        if self.account is not None:
            return "Cannot set issuer if account is set"
        if self.currency is not None and self.currency.upper() == "XRP":
            return "Cannot set issuer if currency is XRP"
        if (
            _is_valid_mptid(self.mpt_issuance_id)
            and isinstance(self.issuer, str)
            # rippled accepts the issuer as a classic address or a hex AccountID
            and self.issuer != get_mpt_issuer(self.mpt_issuance_id)
            and self.issuer.upper() != self.mpt_issuance_id[8:].upper()
        ):
            return "Issuer must match the issuer encoded in mpt_issuance_id"
        return None

    def _get_mpt_issuance_id_error(self: Self) -> Optional[str]:
        if self.mpt_issuance_id is None:
            return None
        if self.currency is not None:
            return "Cannot set both currency and mpt_issuance_id"
        if not _is_valid_mptid(self.mpt_issuance_id):
            return f"Invalid mpt_issuance_id {self.mpt_issuance_id}"
        return None


Path = List[PathStep]
"""
A Path is an ordered array of PathSteps.
"""
