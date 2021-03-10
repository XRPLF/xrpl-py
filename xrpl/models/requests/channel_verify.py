"""
The channel_verify method checks the validity of a
signature that can be used to redeem a specific amount of
XRP from a payment channel.
"""
from dataclasses import dataclass, field

from xrpl.models.base_model import REQUIRED
from xrpl.models.requests.request import Request, RequestMethod


@dataclass(frozen=True)
class ChannelVerify(Request):
    """
    The channel_verify method checks the validity of a
    signature that can be used to redeem a specific amount of
    XRP from a payment channel.
    """

    method: RequestMethod = field(default=RequestMethod.CHANNEL_VERIFY, init=False)
    channel_id: str = REQUIRED
    amount: str = REQUIRED
    public_key: str = REQUIRED
    signature: str = REQUIRED
