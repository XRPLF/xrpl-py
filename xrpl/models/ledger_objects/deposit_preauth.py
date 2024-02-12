"""Models for the Ledger Object `DepositPreauth`"""

from __future__ import annotations

from dataclasses import dataclass, field

from xrpl.models.ledger_objects.ledger_entry_type import LedgerEntryType
from xrpl.models.ledger_objects.ledger_object import HasPreviousTxnID, LedgerObject
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class DepositPreauth(LedgerObject, HasPreviousTxnID):
    """The model for the `DepositPreauth` Ledger Object"""

    account: str = REQUIRED  # type: ignore
    """
    The account that granted the preauthorization. (The destination of the
    preauthorized payments.) This field is required.
    """

    authorize: str = REQUIRED  # type: ignore
    """
    The account that received the preauthorization. (The sender of the preauthorized
    payments.) This field is required.
    """

    owner_node: str = REQUIRED  # type: ignore
    """
    A hint indicating which page of the sender's owner directory links to this object,
    in case the directory consists of multiple pages. Note: The object does not contain
    a direct link to the owner directory containing it, since that value can be derived
    from the Account. This field is required.
    """

    ledger_entry_type: LedgerEntryType = field(
        default=LedgerEntryType.DEPOSIT_PREAUTH,
        init=False,
    )
