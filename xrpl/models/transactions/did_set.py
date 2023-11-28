"""Model for DIDSet transaction type."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, Optional, Pattern

from typing_extensions import Final

from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init

HEX_REGEX: Final[Pattern[str]] = re.compile("[a-fA-F0-9]+")


@require_kwargs_on_init
@dataclass(frozen=True)
class DIDSet(Transaction):
    """Represents a DIDSet transaction."""

    did_document: Optional[str] = None
    data: Optional[str] = None
    uri: Optional[str] = None

    transaction_type: TransactionType = field(
        default=TransactionType.DID_SET,
        init=False,
    )

    def _get_errors(self: DIDSet) -> Dict[str, str]:
        errors = super()._get_errors()

        if self.did_document is None and self.data is None and self.uri is None:
            errors["did_set"] = "Must have one of `did_document`, `data`, and `uri`."
            # Can return here because there are no fields to process
            return errors

        def _process_field(name: str, value: Optional[str]) -> None:
            if value is not None:
                error_strs = []
                if not bool(HEX_REGEX.fullmatch(value)):
                    error_strs.append("must be hex")
                if len(value) > 256:
                    error_strs.append("must be <= 256 characters")
                if len(error_strs) > 0:
                    errors[name] = (" and ".join(error_strs) + ".").capitalize()

        _process_field("did_document", self.did_document)
        _process_field("data", self.data)
        _process_field("uri", self.uri)

        return errors
