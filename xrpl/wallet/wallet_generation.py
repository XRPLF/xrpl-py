"""Handles wallet generation from a faucet."""
from time import sleep
from typing import Optional

import requests
from typing_extensions import Final

from xrpl.account import get_balance, get_next_valid_seq_number
from xrpl.clients import Client, XRPLRequestFailureException
from xrpl.constants import XRPLException
from xrpl.wallet.main import Wallet

_TEST_FAUCET_URL: Final[str] = "https://faucet.altnet.rippletest.net/accounts"
_DEV_FAUCET_URL: Final[str] = "https://faucet.devnet.rippletest.net/accounts"

_TIMEOUT_SECONDS: Final[int] = 40
_LEDGER_CLOSE_TIME: Final[int] = 4


class XRPLFaucetException(XRPLException):
    """Faucet generation exception."""

    pass


def generate_faucet_wallet(
    client: Client, wallet: Optional[Wallet] = None, debug: bool = False
) -> Wallet:
    """
    Generates a random wallet and funds it using the XRPL Testnet Faucet.

    Args:
        client: the network client used to make network calls.
        wallet: the wallet to fund. If omitted or `None`, a new wallet is created.
        debug: Whether to print debug information as it creates the wallet.

    Returns:
        A Wallet on the testnet that contains some amount of XRP.

    Raises:
        XRPLFaucetException: if an address could not be funded with the faucet.
        XRPLRequestFailureException: if a request to the ledger fails.
        requests.exceptions.HTTPError: if the request to the faucet fails.

    .. # noqa: DAR402 exception raised in private method
    """
    if "dev" in client.url:  # devnet
        faucet_url = _DEV_FAUCET_URL
    elif "altnet" in client.url or "test" in client.url:  # testnet
        faucet_url = _TEST_FAUCET_URL
    else:
        raise XRPLFaucetException(
            "Cannot fund an account with a client that is not on the testnet or devnet."
        )
    if wallet is None:
        wallet = Wallet.create()

    address = wallet.classic_address
    # The faucet *can* be flakey... by printing info about this it's easier to
    # understand if tests are actually failing, or if it was just a faucet failure.
    if debug:
        print("Attempting to fund address {}".format(address))
    # Balance prior to asking for more funds
    starting_balance = _check_wallet_balance(address, client)

    # Ask the faucet to send funds to the given address
    response = requests.post(url=faucet_url, json={"destination": address})
    if not response.ok:
        response.raise_for_status()
    # Wait for the faucet to fund our account or until timeout
    # Waits one second checks if balance has changed
    # If balance doesn't change it will attempt again until _TIMEOUT_SECONDS
    is_funded = False
    for _ in range(_TIMEOUT_SECONDS):
        sleep(1)
        if not is_funded:  # faucet transaction hasn't been validated yet
            current_balance = _check_wallet_balance(address, client)
            # If our current balance has changed, then the account has been funded
            if current_balance > starting_balance:
                if debug:
                    print("Faucet fund successful.")
                is_funded = True
        else:  # wallet has been funded, now the ledger needs to know the account exists
            next_seq_num = _try_to_get_next_seq(address, client)
            if next_seq_num is not None:
                wallet.sequence = next_seq_num
                return wallet

    raise XRPLFaucetException(
        "Unable to fund address with faucet after waiting {} seconds".format(
            _TIMEOUT_SECONDS
        )
    )


def _check_wallet_balance(address: str, client: Client) -> int:
    try:
        return get_balance(address, client)
    except XRPLRequestFailureException as e:
        if e.error == "actNotFound":  # transaction has not gone through
            return 0
        else:  # some other error
            raise


def _try_to_get_next_seq(address: str, client: Client) -> Optional[int]:
    try:
        return get_next_valid_seq_number(address, client)
    except XRPLRequestFailureException as e:
        if e.error == "actNotFound":
            # faucet gen has not fully gone through, try again
            return None
        else:  # some other error
            raise
