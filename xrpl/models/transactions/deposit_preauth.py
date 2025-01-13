"""Model for DepositPreauth transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from typing_extensions import Self

from xrpl.models.nested_model import NestedModel
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import (
    KW_ONLY_DATACLASS,
    MAX_CREDENTIAL_ARRAY_LENGTH,
    require_kwargs_on_init,
)


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class DepositPreauth(Transaction):
    """
    Represents a `DepositPreauth <https://xrpl.org/depositpreauth.html>`_
    transaction, which gives another account pre-approval to deliver payments to
    the sender of this transaction, if this account is using
    `Deposit Authorization <https://xrpl.org/depositauth.html>`_.
    """

    authorize: Optional[str] = None
    """
    Grant preauthorization to this address. You must provide this OR
    ``unauthorize`` but not both.
    """

    unauthorize: Optional[str] = None
    """
    Revoke preauthorization from this address. You must provide this OR
    ``authorize`` but not both.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.DEPOSIT_PREAUTH,
        init=False,
    )

    authorize_credentials: Optional[List[Credential]] = None
    """The credential(s) that received the preauthorization. (Any account with these
    credentials can send preauthorized payments)."""

    unauthorize_credentials: Optional[List[Credential]] = None
    """The credential(s) whose preauthorization should be revoked."""

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()
        if self.authorize and self.unauthorize:
            errors["DepositPreauth"] = (
                "One of authorize and unauthorize must be set, not both."
            )

        if (
            self.authorize is None
            and self.unauthorize is None
            and self.authorize_credentials is None
            and self.unauthorize_credentials is None
        ):
            errors["DepositPreauth"] = (
                "Exactly one field must be set for either authorize, unauthorize, "
                + "authorize_credentials or unauthorize_credentials. It is "
                + "invalid if none of the params are specified."
            )

        # Filter for input parameters which are provided in the transaction
        # Optional fields in the transaction model are set to None
        params = [
            self.authorize,
            self.unauthorize,
            self.authorize_credentials,
            self.unauthorize_credentials,
        ]
        if sum(param is not None for param in params) > 1:
            errors["DepositPreauth"] = (
                "DepositPreauth txn accepts exactly one input amongst `authorize`, "
                + "`unauthorize`, `authorize_credentials` and `unauthorize_credentials`"
                + "."
            )

        def _validate_credentials_length(
            credentials: List[Credential], field_name: str
        ) -> None:
            if credentials is None:
                return

            if len(credentials) == 0:
                errors["DepositPreauth"] = f"{field_name} list cannot be empty. "
            elif len(credentials) > MAX_CREDENTIAL_ARRAY_LENGTH:
                errors["DepositPreauth"] = (
                    f"{field_name} list cannot exceed "
                    + str(MAX_CREDENTIAL_ARRAY_LENGTH)
                    + " elements. "
                )

            if len(credentials) != len(set(credentials)):
                errors["DepositPreauth"] = (
                    f"{field_name} list cannot contain duplicate credentials."
                )

        if self.authorize_credentials is not None:
            _validate_credentials_length(
                self.authorize_credentials, "AuthorizeCredentials"
            )

        if self.unauthorize_credentials is not None:
            _validate_credentials_length(
                self.unauthorize_credentials, "UnauthorizeCredentials"
            )

        return errors


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class Credential(NestedModel):
    """
    An inner object representing individual element inside AuthorizeCredentials and
    UnauthorizeCredentials array.
    """

    issuer: str = REQUIRED  # type: ignore
    """The issuer of the credential."""

    credential_type: str = REQUIRED  # type: ignore
    """A hex-encoded value to identify the type of credential from the issuer."""
