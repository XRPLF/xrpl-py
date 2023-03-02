"""High-level reliable submission methods with XRPL transactions."""

import asyncio

from typing_extensions import Final

from xrpl.asyncio.clients import Client
from xrpl.asyncio.ledger import get_latest_validated_ledger_sequence
from xrpl.asyncio.transaction.main import _check_fee
from xrpl.asyncio.transaction.main import autofill as _autofill
from xrpl.asyncio.transaction.main import sign, submit
from xrpl.clients import XRPLRequestFailureException
from xrpl.constants import XRPLException
from xrpl.models.requests import Tx
from xrpl.models.response import Response
from xrpl.models.transactions.transaction import Transaction
from xrpl.wallet.main import Wallet

_LEDGER_CLOSE_TIME: Final[int] = 1


class XRPLReliableSubmissionException(XRPLException):
    """General XRPL Reliable Submission Exception."""

    pass


async def _wait_for_final_transaction_outcome(
    transaction_hash: str, client: Client, prelim_result: str, attempts: int = 0
) -> Response:
    """
    The core logic of reliable submission.  Polls the ledger until the result of the
    transaction can be considered final, meaning it has either been included in a
    validated ledger, or the transaction's lastLedgerSequence has been surpassed by the
    latest ledger sequence (meaning it will never be included in a validated ledger).
    """
    await asyncio.sleep(_LEDGER_CLOSE_TIME)
    # new persisted transaction

    # query transaction by hash
    try:
        transaction_response = await client._request_impl(
            Tx(transaction=transaction_hash)
        )
    except XRPLRequestFailureException as e:
        if e.error == "txnNotFound" and attempts < 4:

            """
            For the case if a submitted transaction is still
            in queue and not processed on the ledger yet.
            Retry 4 times before raising an exception.
            """
            return await _wait_for_final_transaction_outcome(
                transaction_hash, client, prelim_result, attempts + 1
            )
        else:
            raise e
    result = transaction_response.result
    if "validated" in result and result["validated"]:
        # result is in a validated ledger, outcome is final
        return transaction_response

    last_ledger_sequence = result["LastLedgerSequence"]
    latest_ledger_sequence = await get_latest_validated_ledger_sequence(client)

    if last_ledger_sequence > latest_ledger_sequence:
        # outcome is not yet final
        return await _wait_for_final_transaction_outcome(
            transaction_hash, client, prelim_result, 0
        )

    raise XRPLReliableSubmissionException(
        f"The latest ledger sequence {latest_ledger_sequence} is greater than the "
        f"last ledger sequence {last_ledger_sequence} in the transaction. Prelim "
        f"result: {prelim_result}"
    )


async def send_reliable_submission(
    transaction: Transaction, client: Client
) -> Response:
    """
    Asynchronously submits a transaction and verifies that it has been included in a
    validated ledger (or has errored/will not be included for some reason).

    `See Reliable Transaction Submission
    <https://xrpl.org/reliable-transaction-submission.html>`_

    Note: This cannot be used with a standalone rippled node, because ledgers do not
    close automatically.

    Args:
        transaction: the signed transaction to submit to the ledger. Requires a
            `last_ledger_sequence` param.
        client: the network client used to submit the transaction to a rippled node.

    Returns:
        The response from a validated ledger.

    Raises:
        XRPLReliableSubmissionException: if the transaction fails, is malformed, or is
            missing a `last_ledger_sequence` param.
    """
    if transaction.last_ledger_sequence is None:
        raise XRPLReliableSubmissionException(
            "Transaction must have a `last_ledger_sequence` param."
        )
    transaction_hash = transaction.get_hash()
    submit_response = await submit(transaction, client)
    prelim_result = submit_response.result["engine_result"]
    if prelim_result[0:3] == "tem":
        raise XRPLReliableSubmissionException(
            submit_response.result["engine_result_message"]
        )

    return await _wait_for_final_transaction_outcome(
        transaction_hash, client, prelim_result, 0
    )


def _is_signed(transaction: Transaction) -> bool:
    """
    Checks if a transaction has been signed.

    Args:
        transaction: the transaction to check.

    Returns:
        Whether the transaction has been signed
    """
    return (
        transaction.signing_pub_key is not None or transaction.txn_signature is not None
    )


async def _get_signed_tx(
    transaction: Transaction,
    wallet: Wallet,
    client: Client,
    check_fee: bool = True,
    autofill: bool = True,
) -> Transaction:
    """
    Initializes a transaction for a submit request.

    Args:
        transaction: the transaction to be submitted.
        wallet: the wallet with which to sign the transaction.
        client: the network client with which to submit the transaction.
        check_fee: whether to check if the fee is higher than the expected transaction
            type fee. Defaults to True.
        autofill: an optional boolean indicating whether to autofill the transaction.

    Returns:
        The signed transaction.
    """
    if _is_signed(transaction):
        return transaction

    if check_fee:
        await _check_fee(transaction, client)

    if autofill:
        transaction = await _autofill(transaction, client)
    return await sign(transaction, wallet, False)


async def submit_and_wait(
    transaction: Transaction,
    wallet: Wallet,
    client: Client,
    check_fee: bool = True,
    autofill: bool = True,
) -> Response:
    """
    Signs a transaction (locally, without trusting external rippled nodes), submits,
    and verifies that it has been included in a validated ledger (or has errored
    /will not be included for some reason).
    `See Reliable Transaction Submission
    <https://xrpl.org/reliable-transaction-submission.html>`_

    Args:
        transaction: the transaction to be signed and submitted.
        wallet: the wallet with which to sign the transaction.
        client: the network client with which to submit the transaction.
        check_fee: whether to check if the fee is higher than the expected transaction
            type fee. Defaults to True.
        autofill: an optional boolean indicating whether to autofill the transaction.

    Returns:
        The response from the ledger.
    """
    signed_transaction = await _get_signed_tx(
        transaction, wallet, client, check_fee, autofill
    )
    return await send_reliable_submission(signed_transaction, client)
