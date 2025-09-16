"""Represents a VaultSet transaction on the XRP Ledger."""

from dataclasses import dataclass, field
from typing import Dict, Optional

from typing_extensions import Self

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.transactions.vault_create import (
    VAULT_MAX_DATA_LENGTH,
    VAULT_MAX_DOMAIN_ID_LENGTH,
)
from xrpl.models.transactions.vault_delete import _MAX_VAULT_ID_LENGTH
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class VaultSet(Transaction):
    """The VaultSet updates an existing Vault ledger object."""

    vault_id: str = REQUIRED
    """The ID of the Vault to be modified. Must be included when updating the Vault."""

    domain_id: Optional[str] = None
    """The PermissionedDomain object ID associated with the shares of this Vault."""

    data: Optional[str] = None
    """Arbitrary Vault metadata, limited to 256 bytes."""

    assets_maximum: Optional[str] = None
    """The maximum asset amount that can be held in a vault. The value cannot be lower
    than the current AssetTotal unless the value is 0.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.VAULT_SET,
        init=False,
    )

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()

        if self.data is not None and len(self.data) > VAULT_MAX_DATA_LENGTH:
            errors["data"] = (
                "Data must be less than 256 bytes (alternatively, 512 hex characters)."
            )
        if (
            self.domain_id is not None
            and len(self.domain_id) != VAULT_MAX_DOMAIN_ID_LENGTH
        ):
            errors["domain_id"] = (
                "Invalid domain ID: Length must be 32 characters (64 hex characters)."
            )

        if len(self.vault_id) != _MAX_VAULT_ID_LENGTH:
            errors["vault_id"] = (
                "Invalid vault ID: Length must be 32 characters (64 hex characters)."
            )

        return errors
