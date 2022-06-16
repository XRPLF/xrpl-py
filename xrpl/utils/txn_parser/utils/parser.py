"""Helper functions for parsers."""

from decimal import Decimal
from typing import Any, Dict, List, Union

from xrpl.utils.txn_parser.utils.types import AccountBalance, AccountOfferChange


def get_value(balance: Union[Dict[str, str], str]) -> Decimal:
    """
    Get a currency amount's value.

    Args:
        balance: Account's balance.

    Returns:
        The currency amount's value.
    """
    if isinstance(balance, str):
        return Decimal(balance)
    return Decimal(balance["value"])


def group_by_account(
    account_objects: Union[List[AccountBalance], List[AccountOfferChange]],
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Groups the account objects in one list for each account.

    Args:
        account_objects: All computed objects.

    Returns:
        The grouped computed objects.
    """
    grouped_objects = {}
    for object in account_objects:
        account = object["account"]
        if account not in grouped_objects:
            grouped_objects[account] = []
        grouped_objects[account].append(object)
    return grouped_objects
