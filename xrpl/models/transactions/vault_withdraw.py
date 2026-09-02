"""Represents a VaultWithdraw transaction on the XRP Ledger."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from typing_extensions import Self

from xrpl.models.amounts import Amount
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.transactions.vault_delete import _MAX_VAULT_ID_LENGTH
from xrpl.models.utils import validate_credential_ids


@dataclass(frozen=True, kw_only=True)
class VaultWithdraw(Transaction):
    """The VaultWithdraw transaction withdraws assets in exchange for the vault's
    shares.
    """

    vault_id: str = REQUIRED
    """The ID of the vault from which assets are withdrawn."""

    amount: Amount = REQUIRED
    """The exact amount of Vault asset to withdraw."""

    destination: Optional[str] = None
    """An account to receive the assets. It must be able to receive the asset."""

    destination_tag: Optional[int] = None
    """
    An arbitrary `destination tag
    <https://xrpl.org/source-and-destination-tags.html>`_ that
    identifies the reason for the Payment, or a hosted recipient to pay.
    """

    credential_ids: Optional[List[str]] = None
    """
    Credential(s) to attach for credential-based deposit preauthorization (XLS-70)
    when the destination requires them.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.VAULT_WITHDRAW,
        init=False,
    )

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()

        if len(self.vault_id) != _MAX_VAULT_ID_LENGTH:
            errors["vault_id"] = (
                "Invalid vault ID: Length must be 32 characters (64 hex characters)."
            )

        errors.update(validate_credential_ids(self.credential_ids))

        return errors
