"""Models for the Ledger Object `DID`"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from xrpl.models.ledger_objects.ledger_entry_type import LedgerEntryType
from xrpl.models.ledger_objects.ledger_object import HasPreviousTxnID, LedgerObject
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class DID(LedgerObject, HasPreviousTxnID):
    """The model for the `DID` Ledger Object"""

    account: str = REQUIRED  # type: ignore
    """
    The account that controls the DID. This field is required.
    """

    did_document: Optional[str] = None
    """
    The W3C standard DID document associated with the DID. The `DIDDocument` field isn't
    checked for validity and is limited to a maximum length of 256 bytes.
    """

    data: Optional[str] = None
    """
    The public attestations of identity credentials associated with the DID. The `Data`
    field isn't checked for validity and is limited to a maximum length of 256 bytes.
    """

    owner_node: str = REQUIRED  # type: ignore
    """
    A hint indicating which page of the sender's owner directory links to this entry,
    in case the directory consists of multiple pages.
    """

    uri: Optional[str] = None
    """
    The Universal Resource Identifier that points to the corresponding DID document or
    the data associated with the DID. This field can be an HTTP(S) URL or IPFS URI.
    This field isn't checked for validity and is limited to a maximum length of 256
    bytes.
    """

    ledger_entry_type: LedgerEntryType = field(
        default=LedgerEntryType.DID,
        init=False,
    )
