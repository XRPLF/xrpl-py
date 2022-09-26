"""A snippet that walks us through an example usage of RegularKey."""
from xrpl.account import get_balance
from xrpl.clients import JsonRpcClient
from xrpl.models.transactions import Payment, SetRegularKey
from xrpl.transaction import (
    safe_sign_and_autofill_transaction,
    send_reliable_submission,
)
from xrpl.wallet import generate_faucet_wallet


def set_regular_key() -> None:
    """
    Sync snippet that walks us through an example usage of RegularKey.
    """
    client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")

    # creating wallets as prerequisite
    wallet1 = generate_faucet_wallet(client, debug=True)
    wallet2 = generate_faucet_wallet(client, debug=True)
    regular_key_wallet = generate_faucet_wallet(client, debug=True)

    print("Balances before payment:")
    print(get_balance(wallet1.classic_address, client))
    print(get_balance(wallet2.classic_address, client))

    # assigns key-pair(regularKeyWallet) to wallet1 using `SetRegularKey`
    tx = SetRegularKey(
        account=wallet1.classic_address, regular_key=regular_key_wallet.classic_address
    )

    signed_tx = safe_sign_and_autofill_transaction(tx, wallet1, client)
    set_regular_key_response = send_reliable_submission(signed_tx, client)

    print("Response for successful SetRegularKey tx")
    print(set_regular_key_response)

    # when wallet1 sends payment to wallet2 andd
    # signs using the regular key wallet, the transaction goes through.
    payment = Payment(
        account=wallet1.classic_address,
        destination=wallet2.classic_address,
        amount="5551000",
    )

    signed_payment = safe_sign_and_autofill_transaction(
        payment, regular_key_wallet, client
    )
    payment_response = send_reliable_submission(signed_payment, client)

    print("Response for tx signed using Regular Key:")
    print(payment_response)

    print("Balances after payment:")
    print(get_balance(wallet1.classic_address, client))
    print(get_balance(wallet2.classic_address, client))


# uncomment the line below to run the snippet
# set_regular_key()
