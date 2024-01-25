"""Models for the Ledger Object `DID`"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from xrpl.models.ledger_objects.ledger_entry_type import LedgerEntryType
from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class DID(LedgerObject):
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

    previous_txn_id: str = REQUIRED  # type: ignore
    """
    The identifying hash of the transaction that most recently modified this object.
    This field is required.
    """

    previous_txn_lgr_seq: int = REQUIRED  # type: ignore
    """
    The index of the ledger that contains the transaction that most recently modified
    this object.
    """

    uri: Optional[str] = None
    """
    The Universal Resource Identifier that points to the corresponding DID document or
    the data associated with the DID. This field can be an HTTP(S) URL or IPFS URI.
    This field isn't checked for validity and is limited to a maximum length of 256
    bytes.
    """

    flags: int = 0
    """
    A bit-map of boolean flags. Flags is always 0 since there are no flags defined for
    DID entries. This field is required.
    """

    ledger_entry_type: LedgerEntryType = field(
        default=LedgerEntryType.DID,
        init=False,
    )
    """
    The value `0x0049`, mapped to the string `DID`, indicates that this object is a DID
    object.
    """
