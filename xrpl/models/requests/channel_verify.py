"""
The channel_verify method checks the validity of a
signature that can be used to redeem a specific amount of
XRP from a payment channel.
"""
from dataclasses import dataclass

from xrpl.models.base_model import REQUIRED
from xrpl.models.requests.request import Request, RequestMethod


@dataclass(frozen=True)
class ChannelVerify(Request):
    """
    The channel_verify method checks the validity of a
    signature that can be used to redeem a specific amount of
    XRP from a payment channel.
    """

    method: RequestMethod = RequestMethod.CHANNEL_VERIFY
    channel_id: str = REQUIRED  # type: ignore
    amount: str = REQUIRED  # type: ignore
    public_key: str = REQUIRED  # type: ignore
    signature: str = REQUIRED  # type: ignore
