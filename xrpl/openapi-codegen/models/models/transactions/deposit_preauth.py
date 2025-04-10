"""Model for DepositPreauth transaction type."""
from dataclasses import dataclass, field
from typing import List, Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.authorize_credentials import AuthorizeCredentials
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class DepositPreauth(Transaction):
    """
    A DepositPreauth transaction grants preauthorization to deliver payments to your
    account. This is only useful if you are using (or plan to use) Deposit Authorization.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.DEPOSIT_PREAUTH,
        init=False
    )

    authorize: Optional[str] = None
    """
    (Optional) An account to preauthorize.
    """

    authorize_credentials: Optional[List[AuthorizeCredentials]] = None
    """
    (Optional) A set of credentials to authorize. (Requires the Credentials amendment.)
    """

    unauthorize: Optional[str] = None
    """
    (Optional) An account whose preauthorization should be revoked.
    """

    unauthorize_credentials: Optional[List[AuthorizeCredentials]] = None
    """
    (Optional) A set of credentials whose preauthorization should be revoked. (Requires the
    Credentials amendment.)
    """

    def _get_errors(self: DepositPreauth) -> Dict[str, str]:
        errors = super._get_errors()
        if self.authorize_credentials is not None and len(self.authorize_credentials) < 1:
            errors["DepositPreauth"] = "Field `authorize_credentials` must have a length greater than or equal to 1"
        if self.authorize_credentials is not None and len(self.authorize_credentials) > 8:
            errors["DepositPreauth"] = "Field `authorize_credentials` must have a length less than or equal to 8"
        if len(self.authorize_credentials) != len(set(self.authorize_credentials)):
            errors["DepositPreauth"] = "`authorize_credentials` list cannot contain duplicate values"
        if self.unauthorize_credentials is not None and len(self.unauthorize_credentials) < 1:
            errors["DepositPreauth"] = "Field `unauthorize_credentials` must have a length greater than or equal to 1"
        if self.unauthorize_credentials is not None and len(self.unauthorize_credentials) > 8:
            errors["DepositPreauth"] = "Field `unauthorize_credentials` must have a length less than or equal to 8"
        if len(self.unauthorize_credentials) != len(set(self.unauthorize_credentials)):
            errors["DepositPreauth"] = "`unauthorize_credentials` list cannot contain duplicate values"
        return errors


