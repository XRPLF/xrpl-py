"""Example of how we can multisign a transaction"""
from xrpl.clients import JsonRpcClient
from xrpl.models.requests import SubmitMultisigned
from xrpl.models.transactions import AccountSet, SignerEntry, SignerListSet
from xrpl.transaction import (
    autofill,
    multisign,
    safe_sign_and_autofill_transaction,
    send_reliable_submission,
    sign_for_multisign,
)
from xrpl.utils import str_to_hex
from xrpl.wallet import generate_faucet_wallet

client = JsonRpcClient("https://s.altnet.rippletest.net:51234")

# Create a wallets to use for multisigning
# Prints debug info as it creates the wallet
master_wallet = generate_faucet_wallet(client, debug=True)
signer_wallet_1 = generate_faucet_wallet(client, debug=True)
signer_wallet_2 = generate_faucet_wallet(client, debug=True)

signer_entries = [
    SignerEntry(account=signer_wallet_1.classic_address, signer_weight=1),
    SignerEntry(account=signer_wallet_2.classic_address, signer_weight=1),
]
signer_list_set_tx = SignerListSet(
    account=master_wallet.classic_address,
    signer_quorum=2,
    signer_entries=signer_entries,
)
signed_signer_list_set_tx = safe_sign_and_autofill_transaction(
    signer_list_set_tx, master_wallet, client
)
print("Constructed SignerListSet and submitting it to the ledger...")
signed_list_set_tx_response = send_reliable_submission(
    signed_signer_list_set_tx, client
)
print("SignerListSet submitted, here's the response:")
print(signed_list_set_tx_response)

# Now that we've set up multisigning, let's try using it to submit an AccountSet
# transaction.
account_set_tx = AccountSet(
    account=master_wallet.classic_address, domain=str_to_hex("example.com")
)
autofilled_account_set_tx = autofill(account_set_tx, client, len(signer_entries))
print("AccountSet transaction is ready to be multisigned")
print(autofilled_account_set_tx)

# A blob is a binary string representation of the transaction that is
# in hex format. We need to encode it into a blob to make it smaller
# for rippled to process.
tx_blob_1 = sign_for_multisign(autofilled_account_set_tx, signer_wallet_1)
tx_blob_2 = sign_for_multisign(autofilled_account_set_tx, signer_wallet_2)

multisigned_tx = multisign(autofilled_account_set_tx, [tx_blob_1, tx_blob_2])

print("Successfully multisigned the transaction")
print(multisigned_tx)

multisigned_tx_response = client.request(SubmitMultisigned(tx_json=multisigned_tx))

if multisigned_tx_response.result["engine_result"] == "tesSUCCESS":
    print("The multisigned transaction was accepted by the ledger:")
    print(multisigned_tx_response)
    if multisigned_tx_response.result["tx_json"]["Signers"]:
        print(
            "The transaction had "
            f"{len(multisigned_tx_response.result['tx_json']['Signers'])} signatures"
        )
else:
    print(
        "The multisigned transaction was rejected by rippled."
        "Here's the response from rippled:"
    )
    print(multisigned_tx_response)
