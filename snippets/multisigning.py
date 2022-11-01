"""Example of how we can multisign a transaction"""
from xrpl.clients import JsonRpcClient
from xrpl.core.binarycodec import encode_for_multisigning
from xrpl.core.keypairs import sign
from xrpl.models.requests import SubmitMultisigned
from xrpl.models.transactions import AccountSet, Signer, SignerEntry, SignerListSet
from xrpl.transaction import (
    autofill,
    safe_sign_and_autofill_transaction,
    send_reliable_submission,
)
from xrpl.utils import str_to_hex
from xrpl.wallet import generate_faucet_wallet

client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")

wallet_master = generate_faucet_wallet(client, debug=True)
signer_wallet_1 = generate_faucet_wallet(client, debug=True)
signer_wallet_2 = generate_faucet_wallet(client, debug=True)

signer_entries = [
    SignerEntry(account=signer_wallet_1.classic_address, signer_weight=1),
    SignerEntry(account=signer_wallet_2.classic_address, signer_weight=1),
]
signer_list_set_tx = SignerListSet(
    account=wallet_master.classic_address,
    signer_quorum=2,
    signer_entries=signer_entries,
)
signed_signer_list_set_tx = safe_sign_and_autofill_transaction(
    signer_list_set_tx, wallet_master, client
)
signed_list_set_tx_response = send_reliable_submission(
    signed_signer_list_set_tx, client
)
print("SignerListSet constructed and submitted, here's the response:")
print(signed_list_set_tx_response)

# Now that we've set up multisigning, let's try using it to submit an AccountSet
# transaction.
account_set_tx = AccountSet(
    account=wallet_master.classic_address, domain=str_to_hex("example.com")
)
autofilled_account_set_tx = autofill(account_set_tx, client, len(signer_entries))
print("AccountSet transaction is ready to be multisigned")
print(autofilled_account_set_tx)

autofilled_account_set_tx_json = autofilled_account_set_tx.to_xrpl()
# A blob is a binary string representation of the transaction that is
# in hex format. We need to encode it into a blob to make it smaller
# for rippled to process.
tx_blob1 = sign(
    bytes.fromhex(
        encode_for_multisigning(
            autofilled_account_set_tx_json,
            signer_wallet_1.classic_address,
        )
    ),
    signer_wallet_1.private_key,
)
tx_blob2 = sign(
    bytes.fromhex(
        encode_for_multisigning(
            autofilled_account_set_tx_json,
            signer_wallet_2.classic_address,
        )
    ),
    signer_wallet_2.private_key,
)

# Individually signing the transaction with each signer.
# This would normally be handled by reaching out to the signing
# account owners in your application since you would not normally
# be in control of all the keys.
autofilled_account_set_tx_dict = autofilled_account_set_tx.to_dict()
autofilled_account_set_tx_dict["signers"] = [
    Signer(
        account=signer_wallet_1.classic_address,
        txn_signature=tx_blob1,
        signing_pub_key=signer_wallet_1.public_key,
    ),
    Signer(
        account=signer_wallet_2.classic_address,
        txn_signature=tx_blob2,
        signing_pub_key=signer_wallet_2.public_key,
    ),
]
multisigned_tx = AccountSet.from_dict(autofilled_account_set_tx_dict)
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
