"""Model for DIDSet transaction type."""
from dataclasses import dataclass, field
from typing import Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class DIDSet(Transaction):
    """
    Creates a new DID ledger entry or updates the fields of an existing one.  To delete the
    Data, DIDDocument, or URI field from an existing DID ledger entry, add the field as an
    empty string.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.DID_SET,
        init=False
    )

    data: Optional[str] = None
    """
    (Optional) The public attestations of identity credentials associated with the DID.
    """

    did_document: Optional[str] = None
    """
    (Optional) The DID document associated with the DID.
    """

    uri: Optional[str] = None
    """
    (Optional) The Universal Resource Identifier associated with the DID.
    """

    def _get_errors(self: DIDSet) -> Dict[str, str]:
        errors = super._get_errors()
        if (
            self.data is None and
            self.did_document is None and
            self.uri is None
        ):
            errors["DIDSet"] = "At least one of `data`, `did_document`, `uri` must be set."
        if self.data is not None and len(self.data) > 256:
            errors["DIDSet"] = "Field `data` must have a length less than or equal to 256"
        if self.did_document is not None and len(self.did_document) > 256:
            errors["DIDSet"] = "Field `did_document` must have a length less than or equal to 256"
        if self.uri is not None and len(self.uri) > 256:
            errors["DIDSet"] = "Field `uri` must have a length less than or equal to 256"
        return errors


