"""
The manifest method reports the current
"manifest" information for a given validator
public key. The "manifest" is the public portion
of that validator's configured token.
"""
from dataclasses import dataclass

from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.required import REQUIRED


@dataclass(frozen=True)
class Manifest(Request):
    """
    The manifest method reports the current
    "manifest" information for a given validator
    public key. The "manifest" is the public portion
    of that validator's configured token.
    """

    method: RequestMethod = RequestMethod.MANIFEST
    public_key: str = REQUIRED
