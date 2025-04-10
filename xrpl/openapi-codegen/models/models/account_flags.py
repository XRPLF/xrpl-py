"""Model for AccountFlags."""

from dataclasses import dataclass
from typing import Optional
from xrpl.models.base_model import BaseModel
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class AccountFlags(BaseModel):
    default_ripple: Optional[bool] = None
    """
    If true, the account allows rippling on its trust lines by default.
    """

    deposit_auth: Optional[bool] = None
    """
    If true, the account is using Deposit Authorization and does not accept any payments
    from unknown parties.
    """

    disable_master_key: Optional[bool] = None
    """
    If true, the account's master key pair is disabled.
    """

    disallow_incoming_check: Optional[bool] = None
    """
    If true, the account does not allow others to send Checks to it.
    """

    disallow_incoming_nf_token_offer: Optional[bool] = None
    """
    If true, the account does not allow others to make NFT buy or sell offers to it.
    """

    disallow_incoming_pay_chan: Optional[bool] = None
    """
    If true, the account does not allow others to make Payment Channels to it.
    """

    disallow_incoming_trustline: Optional[bool] = None
    """
    If true, the account does not allow others to make trust lines to it.
    """

    disallow_incoming_xrp: Optional[bool] = None
    """
    If true, the account does not want to receive XRP from others. This is advisory and not
    enforced at a protocol level.
    """

    global_freeze: Optional[bool] = None
    """
    If true, all tokens issued by the account are currently frozen.
    """

    no_freeze: Optional[bool] = None
    """
    If true, the account has permanently given up the abilities to freeze individual trust
    lines or end a global freeze.
    """

    password_spent: Optional[bool] = None
    """
    If false, the account can send a special key reset transaction with a transaction cost
    of 0.
    """

    require_authorization: Optional[bool] = None
    """
    If true, the account is using Authorized Trust Lines to limit who can hold the tokens it
    issues.
    """

    require_destination_tag: Optional[bool] = None
    """
    If true, the account requires a destination tag on all payments it receives.
    """
