"""Model for AccountChannels request type."""
from dataclasses import dataclass, field
from typing import Any, Optional, Union
from xrpl.models.requests.request import RequestMethod
from xrpl.models.utils import REQUIRED
from xrpl.models.requests.base_request import BaseRequest
from xrpl.models.requests.lookup_by_ledger import LookupByLedgerRequest
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class AccountChannels(BaseRequest, LookupByLedgerRequest):
    """
    The account_channels method returns information about an account's Payment Channels. 
    This includes only channels where the specified account is the channel's source, not the
    destination.  (A channel's source and owner are the same.) All information retrieved is
    relative to a particular version of the ledger.  Returns an AccountChannelsResponse.
    """

    method: RequestMethod = field(default=RequestMethod.ACCOUNT_CHANNELS, init=False)

    account: str = REQUIRED
    """
    The unique identifier of an account, typically the account's address.
    """

    destination_account: Optional[str] = None
    """
    The unique identifier of an account, typically the account's address. If provided,
    filter results to payment channels whose destination is this account.
    """

    limit: Optional[Union[float, int]] = None
    """
    Limit the number of transactions to retrieve. Cannot be less than 10 or more than 400.
    The default is 200.
    """

    marker: Optional[Any] = None
    """
    Value from a previous paginated response. Resume retrieving data where that response
    left off.
    """

    def _get_errors(self: AccountChannels) -> Dict[str, str]:
        errors = super._get_errors()
        if self.limit is not None and self.limit < 10:
            errors["AccountChannels"] = "Field `limit` must have a value greater than or equal to 10"
        if self.limit is not None and self.limit > 400:
            errors["AccountChannels"] = "Field `limit` must have a value less than or equal to 400"
        return errors


