"""Model for SignAndSubmitModeV1."""

from dataclasses import dataclass
from typing import Any, Dict
from xrpl.models.utils import REQUIRED
from xrpl.models.sign_and_submit_mode_base import SignAndSubmitModeBase
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class SignAndSubmitModeV1(SignAndSubmitModeBase):
    tx_json: Dict[str, Any] = REQUIRED
    """
    Transaction definition in JSON format, optionally omitting any auto-fillable fields.
    """
