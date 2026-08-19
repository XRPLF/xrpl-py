"""Model for PathStep."""

from dataclasses import dataclass
from typing import Optional
from xrpl.models.base_model import BaseModel
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class PathStep(BaseModel):
    """
    A PathStep represents an individual step along a Path.
    """

    account: Optional[str] = None
    """
    (Optional) If present, this path step represents rippling through the specified address.
    MUST NOT be provided if this step specifies the currency or issuer fields.
    """

    currency: Optional[str] = None
    """
    (Optional) If present, this path step represents changing currencies through an order
    book. The currency specified indicates the new currency. MUST NOT be provided if this
    step specifies the account field.
    """

    issuer: Optional[str] = None
    """
    (Optional) If present, this path step represents changing currencies and this address
    defines the issuer of the new currency. If omitted in a step with a non-XRP currency, a
    previous step of the path defines the issuer. If present when currency is omitted,
    indicates a path step that uses an order book between same-named currencies with
    different issuers. MUST be omitted if the currency is XRP. MUST NOT be provided if this
    step specifies the account field.
    """

    type: Optional[int] = None
    """
    DEPRECATED (Optional) An indicator of which other fields are present.
    """

    type_hex: Optional[str] = None
    """
    DEPRECATED: (Optional) A hexadecimal representation of the type field.
    """
