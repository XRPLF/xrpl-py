"""
Represents a SetHook transaction on the XRP Ledger.
Creates or modifies a hook.

`See SetHook <https://xrpl.org/sethook.html>`_
"""
from dataclasses import dataclass, field

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class SetHook(Transaction):
    """
    Represents a SetHook transaction on the XRP Ledger.
    Creates or modifies a hook.

    `See SetHook <https://xrpl.org/sethook.html>`_
    """

    create_code: str = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """

    hook_on: str = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """

    transaction_type: TransactionType = field(
        default=TransactionType.SET_HOOK,
        init=False,
    )
