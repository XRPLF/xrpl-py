"""CLI command for setting up a bridge."""

from pprint import pprint
from time import sleep

from xrpl.account import does_account_exist, get_balance
from xrpl.clients import JsonRpcClient
from xrpl.models import (
    AccountObjects,
    AccountObjectType,
    XChainAccountCreateCommit,
    XChainBridge,
    XChainCommit,
    XChainCreateClaimID,
)
from xrpl.transaction import submit_and_wait
from xrpl.utils import get_xchain_claim_id, xrp_to_drops
from xrpl.wallet import Wallet, generate_faucet_wallet

locking_client = JsonRpcClient("https://s.devnet.rippletest.net:51234")
issuing_client = JsonRpcClient("https://sidechain-net2.devnet.rippletest.net:51234")

locking_chain_door = "rNQQyL2bJqbtgP5zXHJyQXamtrKYpgsbzV"
bridge_data = locking_client.request(
    AccountObjects(account=locking_chain_door, type=AccountObjectType.BRIDGE)
).result["account_objects"][0]
bridge = XChainBridge.from_xrpl(bridge_data["XChainBridge"])
print(bridge)

print("Funding a wallet via the faucet on the locking chain...")
wallet1 = generate_faucet_wallet(locking_client, debug=True)
print(wallet1)
wallet2 = Wallet.create()

print(f"Creating {wallet2.classic_address} on the issuing chain via the bridge...")

fund_tx = XChainAccountCreateCommit(
    account=wallet1.classic_address,
    xchain_bridge=bridge,
    signature_reward=bridge_data["SignatureReward"],
    destination=wallet2.classic_address,
    amount=str(int(bridge_data["MinAccountCreateAmount"]) * 2),
)
fund_response = submit_and_wait(fund_tx, locking_client, wallet1)
pprint(fund_response.result)


print("Waiting for the attestation to go through on the issuing chain...")
ledgers_waited = 0
MAX_LEDGERS_WAITED = 5
while ledgers_waited < MAX_LEDGERS_WAITED:
    sleep(4)
    if does_account_exist(wallet2.classic_address, issuing_client):
        print(
            f"Destination account {wallet2.classic_address} has been created via the "
            "bridge"
        )
        initial_balance = get_balance(wallet2.classic_address, issuing_client)
        break

    ledgers_waited += 1
    if ledgers_waited == MAX_LEDGERS_WAITED:
        raise Exception("Destination account creation via the bridge failed.")

print(
    "Submitting XChainCreateClaimID transaction on the issuing chain to get an "
    "XChainOwnedClaimID for the transfer..."
)
create_claim_id_tx = XChainCreateClaimID(
    account=wallet2.classic_address,
    xchain_bridge=bridge,
    signature_reward=bridge_data["SignatureReward"],
    other_chain_source=wallet1.classic_address,
)
create_claim_id_result = submit_and_wait(create_claim_id_tx, issuing_client, wallet2)
pprint(create_claim_id_result.result)

# Extract new sequence number from metadata
xchain_claim_id = get_xchain_claim_id(create_claim_id_result.result["meta"])

# XChainCommit

print("Sending XChainCommit tx to lock the funds for transfer...")
commit_tx = XChainCommit(
    account=wallet1.classic_address,
    amount=xrp_to_drops(1),
    xchain_bridge=bridge,
    xchain_claim_id=xchain_claim_id,
    other_chain_destination=wallet2.classic_address,
)
commit_result = submit_and_wait(commit_tx, locking_client, wallet1)
pprint(commit_result.result)

print("Waiting for the attestation to go through on the issuing chain...")
ledgers_waited = 0
while ledgers_waited < MAX_LEDGERS_WAITED:
    sleep(4)
    current_balance = get_balance(wallet2.classic_address, issuing_client)
    if current_balance != initial_balance:
        print("Transfer is complete!")
        break

    ledgers_waited += 1
    if ledgers_waited == MAX_LEDGERS_WAITED:
        raise Exception("Bridge transfer failed.")
