"""Handles wallet generation from a faucet."""

from time import sleep

from requests import post

from xrpl import XRPLException
from xrpl.account import get_balance, get_next_valid_seq_number
from xrpl.clients import Client, XRPLRequestFailureException
from xrpl.wallet.main import Wallet

_TEST_FAUCET_URL = "https://faucet.altnet.rippletest.net/accounts"
_DEV_FAUCET_URL = "https://faucet.devnet.rippletest.net/accounts"

_TIMEOUT_SECONDS = 40
_LEDGER_CLOSE_TIME = 4


class XRPLFaucetException(XRPLException):
    """Faucet generation exception."""

    pass


def generate_faucet_wallet(client: Client, debug: bool = False) -> Wallet:
    """
    Generates a random wallet and funds it using the XRPL Testnet Faucet.

    Args:
        client: the network client used to make network calls.
        debug: Whether to print debug information as it creates the wallet.

    Returns:
        A Wallet on the testnet that contains some amount of XRP.

    Raises:
        XRPLFaucetException: if an address could not be funded with the faucet.
        XRPLRequestFailureException: if a request to the ledger fails.
    """
    if "dev" in client.url:  # devnet
        faucet_url = _DEV_FAUCET_URL
    elif "altnet" in client.url or "test" in client.url:  # testnet
        faucet_url = _TEST_FAUCET_URL
    else:
        raise XRPLFaucetException(
            "Cannot fund an account with a client that is not on the testnet or devnet."
        )
    wallet = Wallet.create()

    address = wallet.classic_address
    # The faucet *can* be flakey... by printing info about this it's easier to
    # understand if tests are actually failing, or if it was just a faucet failure.
    if debug:
        print("Attempting to fund address {}".format(address))
    # Balance prior to asking for more funds
    try:
        starting_balance = get_balance(address, client)
    except XRPLRequestFailureException:
        starting_balance = 0

    # Ask the faucet to send funds to the given address
    post(url=faucet_url, json={"destination": address})
    # Wait for the faucet to fund our account or until timeout
    # Waits one second checks if balance has changed
    # If balance doesn't change it will attempt again until _TIMEOUT_SECONDS
    for _ in range(_TIMEOUT_SECONDS):
        sleep(1)
        try:
            current_balance = get_balance(address, client)
        except XRPLRequestFailureException:
            current_balance = 0
        # If our current balance has not changed, then try again
        if current_balance <= starting_balance:
            continue
        if debug:
            print("Faucet fund successful.")
        try:
            wallet.next_sequence_num = get_next_valid_seq_number(address, client)
        except XRPLRequestFailureException as e:
            if e.error_code == "actNotFound":
                sleep(_LEDGER_CLOSE_TIME)
                wallet.next_sequence_num = get_next_valid_seq_number(address, client)
            else:
                raise
        return wallet

    # Otherwise, timeout before balance updates
    raise XRPLFaucetException(
        "Unable to fund address with faucet after waiting {} seconds".format(
            _TIMEOUT_SECONDS
        )
    )
