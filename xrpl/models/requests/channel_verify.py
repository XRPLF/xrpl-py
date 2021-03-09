"""
The channel_verify method checks the validity of a
signature that can be used to redeem a specific amount of
XRP from a payment channel.
"""
from dataclasses import dataclass

from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.required import REQUIRED


@dataclass(frozen=True)
class ChannelVerify(Request):
    """
    The channel_verify method checks the validity of a
    signature that can be used to redeem a specific amount of
    XRP from a payment channel.
    """

    method: RequestMethod = RequestMethod.CHANNEL_VERIFY
    channel_id: str = REQUIRED
    amount: str = REQUIRED
    public_key: str = REQUIRED
    signature: str = REQUIRED
