"""Additional custom parameters to add to the Client"""
from dataclasses import dataclass
from typing import Optional

from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class ClientParameters:
    """
    Additional custom parameters for the Client to apply specific
    logic or validation.
    """

    # Maximum fee to use in a Transaction, in drops of XRP. Defaults to 2 XRP
    max_fee: Optional[str] = "2000000"
