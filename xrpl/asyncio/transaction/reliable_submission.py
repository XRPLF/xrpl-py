"""High-level reliable submission methods with XRPL transactions."""

import asyncio

from typing_extensions import Final

from xrpl.asyncio.clients import Client
from xrpl.asyncio.ledger import get_latest_validated_ledger_sequence
from xrpl.asyncio.transaction.ledger import get_transaction_from_hash
from xrpl.asyncio.transaction.main import submit_transaction
from xrpl.constants import XRPLException
from xrpl.models.response import Response
from xrpl.models.transactions.transaction import Transaction

_LEDGER_CLOSE_TIME: Final[int] = 4


class XRPLReliableSubmissionException(XRPLException):
    """General XRPL Reliable Submission Exception."""

    pass


async def _wait_for_final_transaction_outcome(
    transaction_hash: str, client: Client, prelim_result: str
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
    transaction_response = await get_transaction_from_hash(transaction_hash, client)

    result = transaction_response.result
    if "validated" in result and result["validated"]:
        # result is in a validated ledger, outcome is final
        return transaction_response

    last_ledger_sequence = result["LastLedgerSequence"]
    latest_ledger_sequence = await get_latest_validated_ledger_sequence(client)

    if last_ledger_sequence > latest_ledger_sequence:
        # outcome is not yet final
        return await _wait_for_final_transaction_outcome(
            transaction_hash, client, prelim_result
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
    submit_response = await submit_transaction(transaction, client)
    prelim_result = submit_response.result["engine_result"]
    if prelim_result[0:3] == "tem":
        raise XRPLReliableSubmissionException(
            submit_response.result["engine_result_message"]
        )

    return await _wait_for_final_transaction_outcome(
        transaction_hash, client, prelim_result
    )
