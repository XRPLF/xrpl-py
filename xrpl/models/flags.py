"""All transaction flags and utils to build a list of ints from a FlagInterface"""

from enum import Enum
from typing import Dict, List, Type, Union

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.flag_interface import FlagInterface
from xrpl.models.transactions.types.pseudo_transaction_type import PseudoTransactionType
from xrpl.models.transactions.types.transaction_type import TransactionType


def _get_flag_map(flag_enum: Type[Enum]) -> Dict[str, int]:
    return {flag.name.lower(): flag.value for flag in flag_enum}


def interface_to_flag_list(
    tx_type: Union[TransactionType, PseudoTransactionType],
    tx_flags: FlagInterface,
) -> List[int]:
    """Parse a list of flags expressed as integers from the FlagInterface.

    Args:
        tx_type: Type of the transaction.
        tx_flags: FlagInterface

    Returns:
        List[int]:
            A list of flags expressed as integers.
    """
    from xrpl.models import transactions  # Avoid circular dependencies

    flag_enums = [
        f for f in transactions.__all__ if f.endswith("Flag") and "Asf" not in f
    ]
    pseudo_tx_flag_enums = [
        f
        for f in transactions.pseudo_transactions.__all__
        if f.endswith("Flag") and "Asf" not in f
    ]

    # Key is transaction type name, value is mapping of flag name to int value
    all_tx_flags: Dict[str, Dict[str, int]] = {
        # The `:-4` here removes the `Flag` at the end of the class type to just get
        # the transaction type name
        **{f[:-4]: _get_flag_map(getattr(transactions, f)) for f in flag_enums},
        **{
            f[:-4]: _get_flag_map(getattr(transactions.pseudo_transactions, f))
            for f in pseudo_tx_flag_enums
        },
    }

    if tx_type not in all_tx_flags:
        # if transaction types has no flags
        return [0]

    tx_specific_flags = all_tx_flags[tx_type]  # get flags for that transaction type
    flag_list = []  # accumulator of the flag numbers
    for flag, flag_on in tx_flags.items():
        flag = flag.lower()
        if flag_on:  # if flag was set to True
            if flag in tx_specific_flags:  # if flag was defined
                flag_list.append(tx_specific_flags[flag])
            else:
                flag_list.append(0)  # if flag was set to False
    return flag_list


def check_false_flag_definition(
    tx_type: Union[TransactionType, PseudoTransactionType],
    tx_flags: Union[FlagInterface, List[int]],
) -> None:
    """Check the flags were set correctly if not defined as integer.

    Args:
        tx_type (Union[TransactionType, PseudoTransactionType]):
            Type of the transaction.
        tx_flags (Iterable):
            FlagInterface

    Raises:
        XRPLModelException: Flags were not set correctly.
    """
    try:
        if isinstance(tx_flags, list):  # List[int]
            assert all(isinstance(flag, int) for flag in tx_flags)
        else:  # FlagInterface
            assert all(
                [
                    all(
                        (
                            isinstance(flag, str),
                            isinstance(set_flag, bool),
                        )
                    )
                    for flag, set_flag in tx_flags.items()
                ]
            )
    except AssertionError:
        msg = f"""
False flag definition: Please define flags either by setting bools using
`{tx_type}FlagInterface` or by using `{tx_type}Flag`.
Do not put the FlagInterface in a list or mix them.
""".strip()
        raise XRPLModelException(msg)
