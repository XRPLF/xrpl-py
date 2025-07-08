"""
This request retrieves information about a Single Asset Vault.

All information retrieved is relative to a particular version of the ledger.
"""

from dataclasses import dataclass, field
from typing import Optional

from typing_extensions import Self

from xrpl.models.requests.request import LookupByLedgerRequest, Request, RequestMethod
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class VaultInfo(Request, LookupByLedgerRequest):
    """
    This request retrieves information about a Single Asset Vault.

    All information retrieved is relative to a particular version of the ledger.

    Information about a vault ledger-object can be fetched by providing either the
    vault_id or both owner and seq values. Please check the documentation for more
    details.
    """

    vault_id: Optional[str] = None
    """The object ID of the Vault to be returned."""

    owner: Optional[str] = None
    """The account address of the Vault Owner."""

    seq: Optional[int] = None
    """The transaction sequence number that created the vault."""

    method: RequestMethod = field(default=RequestMethod.VAULT_INFO, init=False)

    def __post_init__(self: Self) -> None:
        """Validate that either vault_id or both owner and seq are provided."""
        if self.vault_id is None and (self.owner is None or self.seq is None):
            raise ValueError(
                "Either vault_id must be provided, or both owner and seq must be "
                "provided"
            )
        if self.vault_id is not None and (
            self.owner is not None or self.seq is not None
        ):
            raise ValueError("Cannot provide both vault_id and owner/seq parameters")
