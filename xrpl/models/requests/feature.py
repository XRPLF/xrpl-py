"""This request gets information about a network's amendments."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from xrpl.models.requests.request import Request, RequestMethod


@dataclass(frozen=True, kw_only=True)
class Feature(Request):
    """The `feature` method gets information about a network's amendments."""

    feature: Optional[str] = None
    """
    The hex-encoded feature hash.
    """

    method: RequestMethod = field(default=RequestMethod.FEATURE, init=False)
