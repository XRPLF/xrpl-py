from time import sleep

from requests import post

from xrpl import CryptoAlgorithm
from xrpl.binarycodec import encode, encode_for_signing
from xrpl.keypairs import derive_classic_address, derive_keypair, generate_seed, sign
from xrpl.models.requests.accounts.account_info import AccountInfo
from xrpl.models.requests.fee import Fee
from xrpl.models.requests.transactions import SubmitOnly
from xrpl.models.response import Response
from xrpl.models.transactions.transaction import Transaction
from xrpl.network_clients.json_rpc_client import (
    JsonRpcClient,
    json_to_response,
    request_to_json_rpc,
)

JSON_RPC_URL = "http://test.xrp.xpring.io:51234"
JSON_RPC_CLIENT = JsonRpcClient(JSON_RPC_URL)

FAUCET_URL = "https://faucet.altnet.rippletest.net/accounts"


class Wallet:
    """The information needed to control an XRPL account."""

    def __init__(self, crypto_algorithm=CryptoAlgorithm.SECP256K1):
        """Generate a new Wallet. Defaults to SECP256K1."""
        self.seed = generate_seed(algorithm=crypto_algorithm)
        self.pub_key, self.priv_key = derive_keypair(self.seed)
        self.classic_address = derive_classic_address(self.pub_key)
        self.next_sequence_num = None

    def __str__(self):
        return (
            f"seed: {self.seed}\npub_key: {self.pub_key}\npriv_key: "
            f"{self.priv_key}\nclassic_address: {self.classic_address}\n"
        )


def submit_transaction(transaction: Transaction, wallet: Wallet) -> Response:
    """Signs and submits a transaction to the XRPL."""
    # Increment the wallet sequence number, since we're about to use one.
    wallet.next_sequence_num += 1
    transaction_json = _prepare_transaction_json_for_binary_codec(transaction.to_dict())
    transaction_json["SigningPubKey"] = wallet.pub_key
    serialized_for_signing = encode_for_signing(transaction_json)
    serialized_bytes = bytes.fromhex(serialized_for_signing)
    signature = sign(serialized_bytes, wallet.priv_key)
    transaction_json["TxnSignature"] = signature
    txn_blob = encode(transaction_json)

    submit_request = SubmitOnly(tx_blob=txn_blob)
    response = post(JSON_RPC_URL, json=request_to_json_rpc(submit_request))
    return json_to_response(response.json())


def generate_faucet_wallet():
    """Generates a random wallet and funds it using the XRPL Testnet Faucet."""
    timeout_seconds = 40
    try:
        wallet = Wallet()
    except Exception as e:
        raise Exception("Could not generate wallet: " + e)

    address = wallet.classic_address
    # The faucet *can* be flakey... by printing info about this it's easier to
    # understand if tests are actually failing, or if it was just a faucet failure.
    print("Attempting to fund address {}".format(address))
    # Balance prior to asking for more funds
    try:
        starting_balance = _get_balance(address)
    except Exception:
        starting_balance = 0

    # Ask the faucet to send funds to the given address
    post(url=FAUCET_URL, json={"destination": address})
    # Wait for the faucet to fund our account or until timeout
    # Waits one second checks if balance has changed
    # If balance doesn't change it will attempt again until timeout_seconds
    for i in range(timeout_seconds):
        sleep(1)
        try:
            current_balance = _get_balance(address)
        except Exception:
            current_balance = 0
        # If our current balance has changed, then return
        if starting_balance != current_balance:
            print("Faucet fund successful.")
            wallet.next_sequence_num = get_next_valid_seq_number(wallet.classic_address)
            return wallet

    # Otherwise, timeout before balance updates
    raise Exception(
        "Unable to fund address with faucet after waiting {} seconds".format(
            timeout_seconds
        )
    )


def get_fee() -> str:
    """Query the ledger for the current minimum transaction fee."""
    fee_request = Fee()
    response = JSON_RPC_CLIENT.request(fee_request)
    return str(response.result["drops"]["minimum_fee"])


def get_next_valid_seq_number(address: str) -> int:
    """Query the ledger for the next available sequence number for an account."""
    account_info = _get_account_info(address)
    return account_info.result["account_data"]["Sequence"]


def _get_balance(address: str) -> int:
    """Query the ledger for the balance of the given account."""
    account_info = _get_account_info(address)
    return int(account_info.result["account_data"]["Balance"])


def _get_account_info(address: str) -> Response:
    """Query the ledger for account info of given address."""
    account_info_request = AccountInfo(
        account=address,
        ledger_index="validated",
    )
    return JSON_RPC_CLIENT.request(account_info_request)


def _prepare_transaction_json_for_binary_codec(dictionary: dict) -> dict:
    """
    Returns a new dictionary in which the keys have been formatted as
    CamelCase and standardized to be serialized by the binary codec.
    """
    formatted_dict = {
        _snake_to_capital_camel(key): value for (key, value) in dictionary.items()
    }
    # one-off conversion cases for transaction field names
    if "CheckId" in formatted_dict:
        formatted_dict["CheckID"] = formatted_dict["CheckId"]
        del formatted_dict["CheckId"]
    if "InvoiceId" in formatted_dict:
        formatted_dict["InvoiceID"] = formatted_dict["InvoiceId"]
        del formatted_dict["InvoiceId"]
    return formatted_dict


def _snake_to_capital_camel(field: str) -> str:
    """Transforms snake case to capitalized camel case.
    For example, 'transaction_type' becomes 'TransactionType'.
    """
    words = field.split("_")
    capitalized_words = [word.capitalize() for word in words]
    return "".join(capitalized_words)
