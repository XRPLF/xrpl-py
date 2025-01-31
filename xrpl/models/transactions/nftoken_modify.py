"""Model for NFTokenModify transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from typing_extensions import Final, Self

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import HEX_REGEX, KW_ONLY_DATACLASS, require_kwargs_on_init

_MAX_URI_LENGTH: Final[int] = 512


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class NFTokenModify(Transaction):
    """
    The NFTokenModify transaction modifies an NFToken's URI
    if its tfMutable is set to true.
    """

    nftoken_id: str = REQUIRED  # type: ignore
    """
    Identifies the TokenID of the NFToken object that the
    offer references. This field is required.
    """

    owner: Optional[str] = None
    """
    Indicates the AccountID of the account that owns the
    corresponding NFToken.
    """

    uri: Optional[str] = None
    """
    URI that points to the data and/or metadata associated with the NFT.
    This field need not be an HTTP or HTTPS URL; it could be an IPFS URI, a
    magnet link, immediate data encoded as an RFC2379 "data" URL, or even an
    opaque issuer-specific encoding. The URI is not checked for validity.

    This field must be hex-encoded. You can use `xrpl.utils.str_to_hex` to
    convert a UTF-8 string to hex.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.NFTOKEN_MODIFY,
        init=False,
    )

    def _get_errors(self: Self) -> Dict[str, str]:
        return {
            key: value
            for key, value in {
                **super()._get_errors(),
                "uri": self._get_uri_error(),
            }.items()
            if value is not None
        }

    def _get_uri_error(self: Self) -> Optional[str]:
        if not self.uri:
            return "URI must not be empty string"
        elif len(self.uri) > _MAX_URI_LENGTH:
            return f"URI must not be longer than {_MAX_URI_LENGTH} characters"

        if not HEX_REGEX.fullmatch(self.uri):
            return "URI must be encoded in hex"
        return None
