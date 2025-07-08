"""Represents a VaultDelete transaction on the XRP Ledger."""

from dataclasses import dataclass, field
from typing import Dict

from typing_extensions import Self

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init

_MAX_VAULT_ID_LENGTH = 64


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class VaultDelete(Transaction):
    """The VaultDelete transaction deletes an existing vault object."""

    vault_id: str = REQUIRED
    """The ID of the vault to be deleted."""

    transaction_type: TransactionType = field(
        default=TransactionType.VAULT_DELETE,
        init=False,
    )

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()

        if len(self.vault_id) != _MAX_VAULT_ID_LENGTH:
            errors["vault_id"] = (
                "Invalid vault ID: Length must be 32 characters (64 hex characters)."
            )

        return errors
