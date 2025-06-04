"""
This request retrieves information about a Single Asset Vault.

All information retrieved is relative to a particular version of the ledger.
"""

from dataclasses import dataclass, field
from typing import Optional

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

    vault_id: Optional[str] = None  # type: ignore
    owner: Optional[str] = None  # type: ignore
    seq: Optional[int] = None  # type: ignore

    method: RequestMethod = field(default=RequestMethod.VAULT_INFO, init=False)
