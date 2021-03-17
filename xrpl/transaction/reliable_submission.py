"""High-level reliable submission methods with XRPL transactions."""

from time import sleep
from typing import Any, Dict, cast

from xrpl.clients import Client
from xrpl.ledger import get_latest_validated_ledger_sequence
from xrpl.models.response import Response
from xrpl.models.transactions.transaction import Transaction
from xrpl.transaction import sign_and_submit_transaction
from xrpl.transaction.exceptions import XRPLReliableSubmissionException
from xrpl.transaction.ledger import get_transaction_from_hash
from xrpl.wallet import Wallet

_LEDGER_CLOSE_TIME = 4


def _wait_for_final_transaction_outcome(
    transaction_hash: str, wallet: Wallet, client: Client
) -> Response:
    """
    The core logic of reliable submission.  Polls the ledger until the result of the
    transaction can be considered final, meaning it has either been included in a
    validated ledger, or the transaction's lastLedgerSequence has been surpassed by the
    latest ledger sequence (meaning it will never be included in a validated ledger).
    """
    sleep(_LEDGER_CLOSE_TIME)
    # new persisted transaction

    # query transaction by hash
    transaction_response = get_transaction_from_hash(transaction_hash, client)

    result = cast(Dict[str, Any], transaction_response.result)
    if "validated" in result and result["validated"]:
        # result is in a validated ledger, outcome is final
        return transaction_response

    last_ledger_sequence = result["LastLedgerSequence"]
    latest_ledger_sequence = get_latest_validated_ledger_sequence(client)

    if last_ledger_sequence > latest_ledger_sequence:
        # outcome is not yet final
        return _wait_for_final_transaction_outcome(transaction_hash, wallet, client)

    raise XRPLReliableSubmissionException(
        f"The latest ledger sequence {latest_ledger_sequence} is greater than the "
        f"last ledger sequence {last_ledger_sequence} in the transaction."
    )


def send_reliable_submission(
    transaction: Transaction, wallet: Wallet, client: Client
) -> Response:
    """
    Submits a transaction and verifies that it has been included in a validated ledger
    (or has errored/will not be included for some reason).

    `See Reliable Transaction Submission
    <https://xrpl.org/reliable-transaction-submission.html>`_

    Args:
        transaction: the transaction to submit to the ledger. Requires a
            `last_ledger_sequence` param.
        wallet: the wallet used to sign the transaction.
        client: the network client used to submit the transaction to a rippled node.

    Returns:
        The response from a validated ledger.

    Raises:
        XRPLReliableSubmissionException: if the transaction fails or is misisng a
            `last_ledger_sequence` param.
    """
    if transaction.last_ledger_sequence is None:
        raise XRPLReliableSubmissionException(
            "Reliable submission requires that the transaction has a "
            "`last_ledger_sequence` parameter."
        )

    submit_response = sign_and_submit_transaction(transaction, wallet, client)
    result = cast(Dict[str, Any], submit_response.result)

    if result["engine_result"] != "tesSUCCESS":
        result_code = result["engine_result"]
        result_message = result["engine_result_message"]
        raise XRPLReliableSubmissionException(
            f"Transaction failed, {result_code}: {result_message}"
        )

    transaction_hash = result["tx_json"]["hash"]
    return _wait_for_final_transaction_outcome(transaction_hash, wallet, client)
