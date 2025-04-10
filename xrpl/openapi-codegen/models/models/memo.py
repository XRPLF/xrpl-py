"""Model for Memo."""

from dataclasses import dataclass
from typing import Optional
from xrpl.models.base_model import BaseModel
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class Memo(BaseModel):
    memo_data: Optional[str] = None
    """
    Arbitrary hex value, conventionally containing the content of the memo.
    """

    memo_format: Optional[str] = None
    """
    Hex value representing characters allowed in URLs. Conventionally containing information
    on how the memo is encoded, for example as a [MIME
    type](https://www.iana.org/assignments/media-types/media-types.xhtml).
    """

    memo_type: Optional[str] = None
    """
    Hex value representing characters allowed in URLs. Conventionally, a unique relation
    (according to [RFC 5988](https://datatracker.ietf.org/doc/html/rfc5988#section-4)) that
    defines the format of this memo.
    """
