"""Model for TokenAmount."""

from dataclasses import dataclass
from typing import Optional
from xrpl.models.base_model import BaseModel
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class TokenAmount(BaseModel):
    """
    Specifies an amount of a (fungible) token.
    """

    currency: Optional[str] = None
    """
    Arbitrary currency code for the token. Cannot be XRP.
    """

    value: Optional[str] = None
    """
    Quoted decimal representation of the amount of the token. This can include scientific
    notation, such as 1.23e11 meaning 123,000,000,000. Both e and E may be used. This can be
    negative when displaying balances, but negative values are disallowed in other contexts
    such as specifying how much to send.
    """

    issuer: Optional[str] = None
    """
    Generally, the account that issues this token. In special cases, this can refer to the
    account that holds the token instead (for example, in a Clawback transaction).
    """

    def _get_errors(self: TokenAmount) -> Dict[str, str]:
        errors = super._get_errors()
        if (
            self.value is not None
            and self.value != REQUIRED
            and not self.value.isnumeric()
        ):
            errors["TokenAmount"] = "`value` must be numeric."
        if not re.match(r"/^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$/", self.value):
            errors["TokenAmount"] = (
                "Field `value` must match the pattern `/^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$/`"
            )
        return errors
