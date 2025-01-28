"""This request simulates a transaction without submitting it to the network."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Type

from typing_extensions import Self

from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class Simulate(Request):
    """
    The `simulate` method simulates a transaction without submitting it to the
    network.
    """

    tx_blob: Optional[str] = None

    transaction: Optional[Transaction] = None

    binary: Optional[bool] = None

    method: RequestMethod = field(default=RequestMethod.SIMULATE, init=False)

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()
        if (self.tx_blob is None) == (self.transaction is None):
            errors["tx"] = (
                "Must have exactly one of `tx_blob` and `transaction` fields."
            )
        return errors

    @classmethod
    def from_dict(cls: Type[Self], value: Dict[str, Any]) -> Self:
        """
        Construct a new Simulate from a dictionary of parameters.

        Args:
            value: The value to construct the Simulate from.

        Returns:
            A new Simulate object, constructed using the given parameters.
        """
        if "tx_json" in value:
            fixed_value = {
                **value,
                "transaction": Transaction.from_xrpl(value["tx_json"]),
            }
            del fixed_value["tx_json"]
        else:
            fixed_value = value
        return super().from_dict(fixed_value)

    def to_dict(self: Self) -> Dict[str, Any]:
        """
        Returns the dictionary representation of a Simulate.

        Returns:
            The dictionary representation of a Simulate.
        """
        return_dict = super().to_dict()
        if self.transaction is not None:
            del return_dict["transaction"]
            return_dict["tx_json"] = self.transaction.to_xrpl()
        return return_dict
