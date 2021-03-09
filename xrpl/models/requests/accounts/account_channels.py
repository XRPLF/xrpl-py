"""
This request returns information about an account's Payment Channels. This includes
only channels where the specified account is the channel's source, not the
destination. (A channel's "source" and "owner" are the same.)

All information retrieved is relative to a particular version of the ledger.

`See account_channels <https://xrpl.org/account_channels.html>`_
"""
from dataclasses import dataclass
from typing import Any, Optional, Union

from xrpl.models.base_model import REQUIRED
from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class AccountChannels(Request):
    """
    This request returns information about an account's Payment Channels. This includes
    only channels where the specified account is the channel's source, not the
    destination. (A channel's "source" and "owner" are the same.)

    All information retrieved is relative to a particular version of the ledger.

    `See account_channels <https://xrpl.org/account_channels.html>`_
    """

    method: RequestMethod = RequestMethod.ACCOUNT_CHANNELS
    account: str = REQUIRED
    destination_account: Optional[str] = None
    limit: int = 200
    # TODO make type
    marker: Optional[Any] = None
    ledger_hash: Optional[str] = None
    ledger_index: Optional[Union[str, int]] = None
