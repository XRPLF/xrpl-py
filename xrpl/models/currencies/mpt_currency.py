"""
Specifies an amount in an issued currency, but without a value field.
This format is used for some book order requests.

See https://xrpl.org/currency-formats.html#specifying-currency-amounts
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Union

from typing_extensions import Self

import xrpl.models.amounts  # not a direct import, to get around circular imports
from xrpl.constants import HEX_MPTID_REGEX
from xrpl.models.base_model import BaseModel
from xrpl.models.required import REQUIRED
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


def _is_valid_mptid(candidate: str) -> bool:
    return bool(HEX_MPTID_REGEX.fullmatch(candidate))


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class MPTCurrency(BaseModel):
    """
    Specifies an amount in an MPT, but without a value field.
    This format is used for some book order requests.

    See https://xrpl.org/currency-formats.html#specifying-currency-amounts
    """

    mpt_issuance_id: str = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()
        if not _is_valid_mptid(self.mpt_issuance_id):
            errors["mpt_issuance_id"] = (
                f"Invalid mpt_issuance_id {self.mpt_issuance_id}"
            )
        return errors

    def to_amount(self: Self, value: Union[str, int]) -> xrpl.models.amounts.MPTAmount:
        """
        Converts an MPTCurrency to an MPTAmount.

        Args:
            value: The amount of MPTs in the MPTAmount.

        Returns:
            An MPTAmount that represents the MPT and the provided value.
        """
        return xrpl.models.amounts.MPTAmount(
            mpt_issuance_id=self.mpt_issuance_id, value=str(value)
        )
