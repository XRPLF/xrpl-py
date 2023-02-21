"""All transacion flags and utils to build a list of ints from a FlagInterface"""

from typing import Dict, List, Union

from typing_extensions import TypedDict

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.types.pseudo_transaction_type import PseudoTransactionType
from xrpl.models.transactions.types.transaction_type import TransactionType

TX_FLAGS: Dict[str, Dict[str, int]] = {
    "AccountSet": {
        "asf_account_tx_id": 0x00000005,
        "asf_authorized_nftoken_minter": 0x0000000A,
        "asf_default_ripple": 0x00000008,
        "asf_deposit_auth": 0x00000009,
        "asf_disable_master": 0x00000004,
        "asf_disallow_xrp": 0x00000003,
        "asf_global_freeze": 0x00000007,
        "asf_no_freeze": 0x00000006,
        "asf_require_auth": 0x00000002,
        "asf_require_dest": 0x00000001,
    },
    "NFTokenCreateOffer": {
        "tf_sell_token": 0x00000001,
    },
    "NFTokenMint": {
        "tf_burnable": 0x00000001,
        "tf_only_xrp": 0x00000002,
        "tf_trustline": 0x00000004,
        "tf_transferable": 0x00000008,
    },
    "OfferCreate": {
        "tf_passive": 0x00010000,
        "tf_immediate_or_cancel": 0x00020000,
        "tf_fill_or_kill": 0x00040000,
        "tf_sell": 0x00080000,
    },
    "Payment": {
        "tf_no_direct_ripple": 0x00010000,
        "tf_partial_payment": 0x00020000,
        "tf_limit_quality": 0x00040000,
    },
    "PaymentChannelClaim": {
        "tf_renew": 0x00010000,
        "tf_close": 0x00020000,
    },
    "TrustSet": {
        "tf_set_auth": 0x00010000,
        "tf_set_no_ripple": 0x00020000,
        "tf_clear_no_ripple": 0x00040000,
        "tf_set_freeze": 0x00100000,
        "tf_clear_freeze": 0x00200000,
    },
    "EnableAmendment": {
        "tf_got_majority": 0x00010000,
        "tf_lost_majority": 0x00020000,
    },
}


class FlagInterface(TypedDict):
    """A TypedDict to define transaction flags by bool."""

    pass


def interface_to_flag_list(
    tx_type: Union[TransactionType, PseudoTransactionType],
    tx_flags: Dict[str, bool],
) -> List[int]:
    """Parse a list of flags expressed as integers from the FlagInterface.

    Args:
        tx_type (Union[TransactionType, PseudoTransactionType]):
            Type of the transaction.
        tx_flags (dict):
            FlagInterface

    Returns:
        List[int]:
            A list of flags expressed as integers.
    """
    if tx_type not in TX_FLAGS:  # if transaction types has no flags
        return [0]
    flags = TX_FLAGS[tx_type]
    flag_list = []
    for flag, num in flags.items():
        if flag in tx_flags:  # if flag was defined
            if tx_flags[flag]:  # if flag was set to True
                flag_list.append(num)
            else:
                flag_list.append(0)  # if flag was set to False
        else:  # if flag was not defined
            flag_list.append(0)
    return flag_list


def check_false_flag_definition(
    tx_type: Union[TransactionType, PseudoTransactionType],
    tx_flags: Union[Dict[str, bool], List[int]],
) -> None:
    """Check the flags were set correctly if not defined as integer.

    Args:
        tx_type (Union[TransactionType, PseudoTransactionType]):
            Type of the transaction.
        tx_flags (Iterable):
            FlagInterface

    Retruns:
        None

    Raises:
        XRPLModelException: Flags were not set correctly.
    """
    try:
        if isinstance(tx_flags, dict):
            interface_flags: Dict[str, bool] = tx_flags
            assert all(
                [
                    all(
                        (
                            isinstance(flag, str),
                            isinstance(set_flag, bool),
                        )
                    )
                    for flag, set_flag in interface_flags.items()
                ]
            )
        else:  # List[int]
            list_flags: List[int] = tx_flags
            assert all(isinstance(flag, int) for flag in list_flags)
    except AssertionError:
        msg = f"""
False flag definition: Please define flags either by setting bools using
`{tx_type}FlagInterface` or by using `{tx_type}Flag`.
Do not put the FlagInterface in a list or mix them.
""".strip()
        raise XRPLModelException(msg)
