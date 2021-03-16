"""High-level reliable submission methods with XRPL transactions."""

from time import sleep
from typing import Any, Dict, cast

from xrpl.clients import Client
from xrpl.models.requests import Ledger, Tx
from xrpl.models.response import Response
from xrpl.models.transactions.transaction import Transaction
from xrpl.reliable_submission.exceptions import LastLedgerSequenceExpiredException
from xrpl.transaction import sign_and_submit_transaction
from xrpl.wallet import Wallet

_LEDGER_CLOSE_TIME = 4


def get_latest_validated_ledger_sequence(client: Client) -> int:
    """
    Returns the sequence number of the latest validated ledger.

    Args:
        client: The network client to use to send the request.

    Returns:
        The sequence number of the latest validated ledger.
    """
    ledger_request = Ledger(ledger_index="validated")
    response = client.request(ledger_request)
    result = cast(Dict[str, Any], response.result)
    return cast(int, result["ledger_index"])


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
    transaction_request = Tx(transaction=transaction_hash)
    transaction_response = client.request(transaction_request)

    result = cast(Dict[str, Any], transaction_response.result)
    if result["validated"]:
        # result is in a validated ledger, outcome is final
        return transaction_response

    last_ledger_sequence = result["LastLedgerSequence"]
    latest_ledger_sequence = get_latest_validated_ledger_sequence(client)

    if last_ledger_sequence > latest_ledger_sequence:
        # outcome is not yet final
        return _wait_for_final_transaction_outcome(transaction_hash, wallet, client)

    raise LastLedgerSequenceExpiredException(
        last_ledger_sequence, latest_ledger_sequence
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
        transaction: the transaction to submit to the ledger.
        wallet: the wallet used to sign the transaction.
        client: the network client used to submit the transaction to a rippled node.

    Returns:
        The response from a validated ledger.
    """
    assert transaction.last_ledger_sequence is not None  # TODO make this a better error
    submit_response = sign_and_submit_transaction(transaction, wallet, client)
    result = cast(Dict[str, Any], submit_response.result)
    transaction_hash = result["tx_json"]["hash"]

    outcome_response = _wait_for_final_transaction_outcome(
        transaction_hash, wallet, client
    )
    return outcome_response
