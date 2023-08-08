"""Model for AMMDelete transaction type."""
from __future__ import annotations

from dataclasses import dataclass, field

from xrpl.models.currencies import Currency
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class AMMDelete(Transaction):
    """TODO: Fill in when docs are ready."""

    asset: Currency = REQUIRED  # type: ignore
    """
    The definition for one of the assets in the AMM's pool. This field is required.
    """

    asset2: Currency = REQUIRED  # type: ignore
    """
    The definition for the other asset in the AMM's pool. This field is required.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.AMM_DELETE,
        init=False,
    )
