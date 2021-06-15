"""
The manifest method reports the current
"manifest" information for a given validator
public key. The "manifest" is the public portion
of that validator's configured token.
"""
from dataclasses import dataclass, field

from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class Manifest(Request):
    """
    The manifest method reports the current
    "manifest" information for a given validator
    public key. The "manifest" is the public portion
    of that validator's configured token.
    """

    method: RequestMethod = field(default=RequestMethod.MANIFEST, init=False)
    public_key: str = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """
