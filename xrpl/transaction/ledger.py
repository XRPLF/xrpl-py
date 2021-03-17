"""High-level methods that fetch transaction information from the XRP Ledger."""

from typing import Any, Dict, cast

from xrpl.clients import Client, XRPLTransactionFailureException
from xrpl.models.requests import AccountTx, Tx
from xrpl.models.response import Response


def get_transaction_from_hash(tx_hash: str, client: Client) -> Response:
    """
    Given a transaction hash, fetch the corresponding transaction from the ledger.

    Args:
        tx_hash: the transaction hash.
        client: the network client used to communicate with a rippled node.

    Returns:
        The Response object containing the transaction info.

    Raises:
        XRPLTransactionFailureException: if the transaction fails.
    """
    response = client.request(Tx(transaction=tx_hash))
    if not response.is_successful():
        result = cast(Dict[str, Any], response.result)
        raise XRPLTransactionFailureException(result["error"], result["error_message"])
    return response


def get_latest_transaction_from_account(account: str, client: Client) -> Response:
    """
    Fetches the most recent transaction on the ledger associated with an account.

    Args:
        account: the classic address of the account.
        client: the network client used to communicate with a rippled node.

    Returns:
        The Response object containing the transaction info.

    Raises:
        XRPLTransactionFailureException: if the transaction fails.
    """
    # max == -1 means that it's the most recent validated ledger version
    response = client.request(AccountTx(account=account, ledger_index_max=-1, limit=1))
    if not response.is_successful():
        result = cast(Dict[str, Any], response.result)
        raise XRPLTransactionFailureException(result["error"], result["error_message"])
    return response
