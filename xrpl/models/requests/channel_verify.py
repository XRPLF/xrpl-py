"""
The channel_verify method checks the validity of a
signature that can be used to redeem a specific amount of
XRP from a payment channel.
"""

from dataclasses import dataclass, field

from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.required import REQUIRED


@dataclass(frozen=True, kw_only=True)
class ChannelVerify(Request):
    """
    The channel_verify method checks the validity of a
    signature that can be used to redeem a specific amount of
    XRP from a payment channel.
    """

    method: RequestMethod = field(default=RequestMethod.CHANNEL_VERIFY, init=False)
    channel_id: str = REQUIRED
    """
    This field is required.

    :meta hide-value:
    """

    amount: str = REQUIRED
    """
    This field is required.

    :meta hide-value:
    """

    public_key: str = REQUIRED
    """
    This field is required.

    :meta hide-value:
    """

    signature: str = REQUIRED
    """
    This field is required.

    :meta hide-value:
    """
