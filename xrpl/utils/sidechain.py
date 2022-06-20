"""Sidechain-related helper util functions."""

from xrpl.constants import XRPLException
from xrpl.models import Memo, Payment
from xrpl.utils.str_conversions import str_to_hex


def create_cross_chain_payment(payment: Payment, dest_account: str) -> Payment:
    """
    Creates a cross-chain payment transaction.

    Args:
        payment: The initial payment transaction. If the transaction is signed, then
            it will need to be re-signed. There must be no more than 2 memos, since the
            first memo is used for the sidechain destination account. The destination
            must be the sidechain's door account.
        dest_account: The destination account on the sidechain.

    Returns:
        A cross-chain payment transaction, where the mainchain door account is the
            `Destination` and the destination account on the sidechain is encoded in
            the memos.

    Raises:
        XRPLException: If there are more than 2 memos.
    """
    dest_account_memo = Memo(memo_data=str_to_hex(dest_account))

    if payment.memos is None:
        memos = []
    else:
        memos = payment.memos
    if memos is not None and len(memos) > 2:
        raise XRPLException(
            "Cannot have more than 2 memos in a cross-chain transaction."
        )
    new_memos = [dest_account_memo] + memos

    payment_dict = payment.to_dict()
    payment_dict["memos"] = new_memos
    if "txn_signature" in payment_dict:
        del payment_dict["txn_signature"]
    return Payment.from_dict(payment_dict)
