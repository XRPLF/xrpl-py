"""Model used in AMMBid transaction."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Type

from xrpl.models.base_model import BaseModel
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class AuthAccount(BaseModel):
    """Represents one entry in a list of AuthAccounts used in AMMBid transaction."""

    account: str = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """

    @classmethod
    def is_dict_of_model(cls: Type[AuthAccount], dictionary: Dict[str, Any]) -> bool:
        """
        Returns True if the input dictionary was derived by the `to_dict`
        method of an instance of this class. In other words, True if this is
        a dictionary representation of an instance of this class.

        NOTE: does not account for model inheritance, IE will only return True
        if dictionary represents an instance of this class, but not if
        dictionary represents an instance of a subclass of this class.

        Args:
            dictionary: The dictionary to check.

        Returns:
            True if dictionary is a dict representation of an instance of this
            class.
        """
        return (
            isinstance(dictionary, dict)
            and "auth_account" in dictionary
            and super().is_dict_of_model(dictionary["auth_account"])
        )

    @classmethod
    def from_dict(cls: Type[AuthAccount], value: Dict[str, Any]) -> AuthAccount:
        """
        Construct a new AuthAccount from a dictionary of parameters.

        Args:
            value: The value to construct the AuthAccount from.

        Returns:
            A new AuthAccount object, constructed using the given parameters.
        """
        if len(value) == 1 and "auth_account" in value:
            return super(AuthAccount, cls).from_dict(value["auth_account"])
        return super(AuthAccount, cls).from_dict(value)

    def to_dict(self: AuthAccount) -> Dict[str, Any]:
        """
        Returns the dictionary representation of a AuthAccount.

        Returns:
            The dictionary representation of a AuthAccount.
        """
        return {"auth_account": super().to_dict()}
