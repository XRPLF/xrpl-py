"""CLI command for setting up a bridge."""

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
from xrpl.utils import xrp_to_drops
from xrpl.wallet import Wallet, generate_faucet_wallet

locking_client = JsonRpcClient("https://sidechain-net1.devnet.rippletest.net:51234")
issuing_client = JsonRpcClient("https://sidechain-net2.devnet.rippletest.net:51234")

locking_chain_door = "rMAXACCrp3Y8PpswXcg3bKggHX76V3F8M4"
bridge_data = locking_client.request(
    AccountObjects(account=locking_chain_door, type=AccountObjectType.BRIDGE)
).result["account_objects"][0]
bridge = XChainBridge.from_xrpl(bridge_data["XChainBridge"])
print(bridge)

wallet1 = generate_faucet_wallet(locking_client, debug=True)
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


# wait for the attestation to go through
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

seq_num_tx = XChainCreateClaimID(
    account=wallet2.classic_address,
    xchain_bridge=bridge,
    signature_reward=bridge_data["SignatureReward"],
    other_chain_source=wallet1.classic_address,
)
seq_num_result = submit_and_wait(seq_num_tx, issuing_client, wallet2)

# # extract new sequence number from metadata
nodes = seq_num_result.result["meta"]["AffectedNodes"]
created_nodes = [node["CreatedNode"] for node in nodes if "CreatedNode" in node.keys()]
claim_ids_ledger_entries = [
    node for node in created_nodes if node["LedgerEntryType"] == "XChainOwnedClaimID"
]
assert len(claim_ids_ledger_entries) == 1, len(claim_ids_ledger_entries)
xchain_claim_id = claim_ids_ledger_entries[0]["NewFields"]["XChainClaimID"]

# # XChainCommit

commit_tx = XChainCommit(
    account=wallet1.classic_address,
    amount=xrp_to_drops(1),
    xchain_bridge=bridge,
    xchain_claim_id=xchain_claim_id,
    other_chain_destination=wallet2.classic_address,
)
submit_and_wait(commit_tx, locking_client, wallet1)

# wait for the attestations to go through
ledgers_waited = 0
while ledgers_waited < MAX_LEDGERS_WAITED:
    sleep(4)
    current_balance = get_balance(wallet2.classic_address, issuing_client)
    if current_balance != initial_balance:
        print("Transfer is complete")
        break

    ledgers_waited += 1
    if ledgers_waited == MAX_LEDGERS_WAITED:
        raise Exception("Bridge transfer failed.")
