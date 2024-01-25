"""Models for the Ledger Object `FeeSettings`"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from xrpl.models.ledger_objects.ledger_entry_type import LedgerEntryType
from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class FeeSettings(LedgerObject):
    """The model for the `FeeSettings` Ledger Object"""

    base_fee: Optional[str] = None
    """
    The transaction cost of the "reference transaction" in drops of XRP as hexadecimal.
    No longer used if XRPFees amendment is enabled.
    """

    reference_fee_units: Optional[int] = None
    """
    The BaseFee translated into "fee units". This field is required.
    """

    reserve_base: Optional[int] = None
    """
    The base reserve for an account in the XRP Ledger, as drops of XRP.
    No longer used if XRPFees amendment is enabled.
    """

    reserve_increment: Optional[int] = None
    """
    The incremental owner reserve for owning objects, as drops of XRP.
    No longer used if XRPFees amendment is enabled.
    """

    base_fee_drops: Optional[str] = None
    """
    The transaction cost of the "reference transaction" in drops of XRP.
    """

    reserve_base_drops: Optional[str] = None
    """
    The base reserve for an account in the XRP Ledger, as drops of XRP.
    """

    reserve_increment_drops: Optional[str] = None
    """
    The incremental owner reserve for owning objects, as drops of XRP.
    """

    flags: int = 0
    """
    A bit-map of boolean flags enabled for this object. Currently, the protocol defines
    no flags for `FeeSettings` objects. The value is always 0. This field is required.
    """

    ledger_entry_type: LedgerEntryType = field(
        default=LedgerEntryType.FEE_SETTINGS, init=False
    )
    """
    The value `0x0073`, mapped to the string `FeeSettings`, indicates that this object
    contains the ledger's fee settings.
    """
