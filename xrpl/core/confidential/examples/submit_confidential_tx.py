#!/usr/bin/env python3
"""
Example: Submit Confidential MPT Transactions

This example demonstrates the complete workflow for confidential MPT transactions
using the high-level transaction builder functions from xrpl.core.confidential.

The workflow includes:
1. Setting up accounts and funding them
2. Creating an MPT issuance with privacy support
3. Converting public tokens to confidential (ConfidentialMPTConvert)
4. Merging inbox to spending balance (ConfidentialMPTMergeInbox)
5. Sending confidential tokens (ConfidentialMPTSend)
6. Converting back to public (ConfidentialMPTConvertBack)

Prerequisites:
- rippled running on localhost:5005 with confidential MPT support
- C bindings built: poetry run poe build_mpt_crypto
- Install with: poetry install --extras confidential

Usage:
    poetry run python xrpl/core/confidential/examples/submit_confidential_tx.py
"""

import sys

from xrpl.clients import JsonRpcClient
from xrpl.constants import CryptoAlgorithm
from xrpl.models.amounts import MPTAmount
from xrpl.models.requests import AccountInfo, GenericRequest
from xrpl.models.transactions import (
    MPTokenAuthorize,
    MPTokenIssuanceCreate,
    MPTokenIssuanceCreateFlag,
    MPTokenIssuanceSet,
    MPTokenIssuanceSetFlag,
    Payment,
)
from xrpl.transaction import sign_and_submit
from xrpl.wallet import Wallet

# Import confidential MPT utilities
try:
    from xrpl.core.confidential import MPTCrypto
    from xrpl.core.confidential.test_utils import (
        check_tx_success,
        fund_account,
        get_mpt_issuance_id,
        print_section,
        print_tx_response,
    )
    from xrpl.core.confidential.transaction_builders import (
        prepare_confidential_convert,
        prepare_confidential_convert_back,
        prepare_confidential_merge_inbox,
        prepare_confidential_send,
    )
    from xrpl.core.confidential.utils import reverse_coordinates
except ImportError as e:
    print(f"ERROR: xrpl.core.confidential not available: {e}")
    print("Build with: poetry run poe build_mpt_crypto")
    sys.exit(1)

# Configuration
RIPPLED_URL = "http://localhost:5005"
MASTER_ACCOUNT = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
MASTER_SECRET = "snoPBrXtMeMyMHUVTgbuqAfg1SUTb"
FUNDING_AMOUNT = "2000000000"  # 2000 XRP in drops

LEDGER_ACCEPT_REQUEST = GenericRequest(method="ledger_accept")


def main():
    """Main example workflow."""
    print_section("Confidential MPT Transaction Example")
    print("Using high-level transaction builder functions\n")

    # Initialize client
    client = JsonRpcClient(RIPPLED_URL)

    # Check server connection
    print_section("Step 1: Setup")
    try:
        client.request(GenericRequest(method="server_info"))
        print("Connected to rippled")
    except Exception as e:
        print(f"ERROR: Failed to connect to rippled: {e}")
        print("Make sure rippled is running on localhost:5005")
        sys.exit(1)

    # Get master account for funding
    print("\nSetting up master account...")
    master_wallet = Wallet.from_seed(MASTER_SECRET, algorithm=CryptoAlgorithm.SECP256K1)

    try:
        account_info = client.request(AccountInfo(account=master_wallet.address))
        balance = int(account_info.result["account_data"]["Balance"]) / 1_000_000
        print(f"Master: {master_wallet.address}")
        print(f"Balance: {balance:,.2f} XRP")
    except Exception as e:
        print(f"ERROR: Master account not found: {e}")
        sys.exit(1)

    # Create test accounts
    print("\nCreating test accounts...")
    issuer_wallet = Wallet.create()
    holder1_wallet = Wallet.create()
    holder2_wallet = Wallet.create()

    print(f"Issuer:  {issuer_wallet.address}")
    print(f"Holder1: {holder1_wallet.address}")
    print(f"Holder2: {holder2_wallet.address}")

    # Fund accounts
    print("\nFunding accounts...")
    fund_account(client, issuer_wallet.address, master_wallet, FUNDING_AMOUNT)
    fund_account(client, holder1_wallet.address, master_wallet, FUNDING_AMOUNT)
    fund_account(client, holder2_wallet.address, master_wallet, FUNDING_AMOUNT)
    print("All accounts funded")

    # Initialize crypto library
    print_section("Step 2: Generate ElGamal Keypairs")
    crypto = MPTCrypto()

    # Generate keypairs with proof of knowledge
    issuer_sk, issuer_pk, issuer_pok = crypto.generate_keypair_with_pok()
    holder1_sk, holder1_pk, holder1_pok = crypto.generate_keypair_with_pok()
    holder2_sk, holder2_pk, holder2_pok = crypto.generate_keypair_with_pok()

    print("Generated ElGamal keypairs")
    print(f"Issuer PK:  {issuer_pk[:32]}... ({len(issuer_pk)//2} bytes)")
    print(f"Holder1 PK: {holder1_pk[:32]}... ({len(holder1_pk)//2} bytes)")
    print(f"Holder2 PK: {holder2_pk[:32]}... ({len(holder2_pk)//2} bytes)")

    # Reverse coordinates for rippled compatibility (for setting on ledger)
    issuer_pk_bytes = bytes.fromhex(issuer_pk)
    holder1_pk_bytes = bytes.fromhex(holder1_pk)
    holder2_pk_bytes = bytes.fromhex(holder2_pk)
    issuer_pk_hex = reverse_coordinates(issuer_pk_bytes).hex().upper()
    holder1_pk_hex = reverse_coordinates(holder1_pk_bytes).hex().upper()
    holder2_pk_hex = reverse_coordinates(holder2_pk_bytes).hex().upper()

    # Create MPT issuance with privacy support
    print_section("Step 3: Create MPT Issuance")
    print("Creating MPT with privacy support...")

    create_issuance_tx = MPTokenIssuanceCreate(
        account=issuer_wallet.address,
        flags=MPTokenIssuanceCreateFlag.TF_MPT_CAN_LOCK
        | MPTokenIssuanceCreateFlag.TF_MPT_CAN_CLAWBACK
        | MPTokenIssuanceCreateFlag.TF_MPT_CAN_TRANSFER
        | MPTokenIssuanceCreateFlag.TF_MPT_CAN_PRIVACY,
        maximum_amount="1000000000000",
        asset_scale=2,
    )

    response = sign_and_submit(create_issuance_tx, client, issuer_wallet)
    print_tx_response(response, "MPTokenIssuanceCreate")
    check_tx_success(response, "MPTokenIssuanceCreate")
    client.request(LEDGER_ACCEPT_REQUEST)

    # Get MPT issuance ID
    mpt_issuance_id = get_mpt_issuance_id(client, issuer_wallet.address)
    print(f"MPT Issuance ID: {mpt_issuance_id}")

    # Set issuer's ElGamal public key
    print("\nSetting issuer's ElGamal public key...")
    set_issuer_pk_tx = MPTokenIssuanceSet(
        account=issuer_wallet.address,
        mptoken_issuance_id=mpt_issuance_id,
        flags=MPTokenIssuanceSetFlag.TF_MPT_UNLOCK,
        issuer_elgamal_public_key=issuer_pk_hex,
    )

    response = sign_and_submit(set_issuer_pk_tx, client, issuer_wallet)
    check_tx_success(response, "MPTokenIssuanceSet (Issuer PK)")
    client.request(LEDGER_ACCEPT_REQUEST)
    print("Issuer ElGamal public key set")

    # Authorize holders
    print_section("Step 4: Authorize Holders")
    for holder_wallet, holder_name in [
        (holder1_wallet, "Holder1"),
        (holder2_wallet, "Holder2"),
    ]:
        print(f"\nAuthorizing {holder_name}...")
        authorize_tx = MPTokenAuthorize(
            account=holder_wallet.address,
            mptoken_issuance_id=mpt_issuance_id,
        )
        response = sign_and_submit(authorize_tx, client, holder_wallet)
        client.request(LEDGER_ACCEPT_REQUEST)
        check_tx_success(response, f"MPTokenAuthorize ({holder_name})")
        print(f"{holder_name} authorized")

    # Issue tokens to Holder1
    print_section("Step 5: Issue Tokens to Holder1")
    issue_amount = 10000

    print(f"\nIssuing {issue_amount} tokens to Holder1...")
    payment_tx = Payment(
        account=issuer_wallet.address,
        destination=holder1_wallet.address,
        amount=MPTAmount(
            mpt_issuance_id=mpt_issuance_id,
            value=str(issue_amount),
        ),
    )

    response = sign_and_submit(payment_tx, client, issuer_wallet)
    check_tx_success(response, "Payment (Issue tokens)")
    client.request(LEDGER_ACCEPT_REQUEST)
    print(f"Issued {issue_amount} tokens to Holder1")

    # Query Holder1's MPT balance to verify
    print("\nQuerying Holder1's MPT balance...")
    from xrpl.models.requests import AccountObjects, AccountObjectType

    holder_objects = client.request(
        AccountObjects(
            account=holder1_wallet.address,
            type=AccountObjectType.MPTOKEN,
        )
    )

    if holder_objects.result.get("account_objects"):
        for obj in holder_objects.result["account_objects"]:
            if obj.get("MPTIssuanceID") == mpt_issuance_id:
                print(f"   MPT Balance: {obj.get('MPTAmount', 'N/A')}")
                print(f"   Full object: {obj}")
                break
    else:
        print("   ⚠️  No MPToken objects found for Holder1")

    # Convert public to confidential (Holder1)
    print_section("Step 6: Convert Public to Confidential (Holder1)")
    convert_amount = 1000

    print(f"\nConverting {convert_amount} tokens to confidential...")
    print("Using prepare_confidential_convert() function...")

    convert_tx = prepare_confidential_convert(
        client=client,
        wallet=holder1_wallet,
        mpt_issuance_id=mpt_issuance_id,
        amount=convert_amount,
        holder_privkey=holder1_sk,
        holder_pubkey=holder1_pk,
        issuer_pubkey=issuer_pk,
    )

    response = sign_and_submit(convert_tx, client, holder1_wallet)
    print_tx_response(response, "ConfidentialMPTConvert")
    check_tx_success(response, "ConfidentialMPTConvert")
    client.request(LEDGER_ACCEPT_REQUEST)
    print(f"Converted {convert_amount} tokens to confidential (inbox)")

    # Merge inbox to spending balance
    print_section("Step 7: Merge Inbox to Spending Balance (Holder1)")
    print("\nMerging inbox to spending balance...")
    print("Using prepare_confidential_merge_inbox() function...")

    merge_tx = prepare_confidential_merge_inbox(
        wallet=holder1_wallet,
        mpt_issuance_id=mpt_issuance_id,
    )

    response = sign_and_submit(merge_tx, client, holder1_wallet)
    print_tx_response(response, "ConfidentialMPTMergeInbox")
    check_tx_success(response, "ConfidentialMPTMergeInbox")
    client.request(LEDGER_ACCEPT_REQUEST)
    print("Inbox merged to spending balance")

    # Register Holder2's ElGamal public key
    print_section("Step 8: Register Holder2's ElGamal Public Key")
    print("\nIssuing 100 tokens to Holder2...")

    payment_holder2_tx = Payment(
        account=issuer_wallet.address,
        destination=holder2_wallet.address,
        amount=MPTAmount(
            mpt_issuance_id=mpt_issuance_id,
            value="100",
        ),
    )
    response = sign_and_submit(payment_holder2_tx, client, issuer_wallet)
    check_tx_success(response, "Payment (Issue tokens to Holder2)")
    client.request(LEDGER_ACCEPT_REQUEST)
    print("Issued 100 tokens to Holder2")

    print("\nHolder2 converting 100 tokens to confidential (registers ElGamal key)...")
    holder2_convert_amount = 100

    holder2_convert_tx = prepare_confidential_convert(
        client=client,
        wallet=holder2_wallet,
        mpt_issuance_id=mpt_issuance_id,
        amount=holder2_convert_amount,
        holder_privkey=holder2_sk,
        holder_pubkey=holder2_pk,
        issuer_pubkey=issuer_pk,
    )

    response = sign_and_submit(holder2_convert_tx, client, holder2_wallet)
    check_tx_success(response, "ConfidentialMPTConvert (Holder2)")
    client.request(LEDGER_ACCEPT_REQUEST)
    print("Holder2 ElGamal key registered")

    # Send confidential tokens
    print_section("Step 9: Send Confidential Tokens")
    send_amount = 300

    print(f"\nSending {send_amount} confidential tokens to Holder2...")
    print("Using prepare_confidential_send() function...")

    send_tx = prepare_confidential_send(
        client=client,
        sender_wallet=holder1_wallet,
        receiver_address=holder2_wallet.address,
        mpt_issuance_id=mpt_issuance_id,
        amount=send_amount,
        sender_privkey=holder1_sk,
        sender_pubkey=holder1_pk,
        receiver_pubkey=holder2_pk,
        issuer_pubkey=issuer_pk,
    )

    response = sign_and_submit(send_tx, client, holder1_wallet)
    print_tx_response(response, "ConfidentialMPTSend")
    check_tx_success(response, "ConfidentialMPTSend")
    client.request(LEDGER_ACCEPT_REQUEST)
    print(f"Sent {send_amount} confidential tokens to Holder2")

    # Merge Holder2's inbox
    print_section("Step 10: Merge Inbox to Spending Balance (Holder2)")
    print("\nMerging Holder2's inbox...")
    merge_tx2 = prepare_confidential_merge_inbox(
        wallet=holder2_wallet,
        mpt_issuance_id=mpt_issuance_id,
    )

    response = sign_and_submit(merge_tx2, client, holder2_wallet)
    check_tx_success(response, "ConfidentialMPTMergeInbox (Holder2)")
    client.request(LEDGER_ACCEPT_REQUEST)
    print("Holder2 inbox merged")

    # Convert back to public
    print_section("Step 11: Convert Back to Public")
    convert_back_amount = 200

    print(f"\nConverting {convert_back_amount} confidential tokens back to public...")
    print("Using prepare_confidential_convert_back() function...")

    convert_back_tx = prepare_confidential_convert_back(
        client=client,
        wallet=holder1_wallet,
        mpt_issuance_id=mpt_issuance_id,
        amount=convert_back_amount,
        holder_privkey=holder1_sk,
        holder_pubkey=holder1_pk,
        issuer_pubkey=issuer_pk,
    )

    response = sign_and_submit(convert_back_tx, client, holder1_wallet)
    print_tx_response(response, "ConfidentialMPTConvertBack")
    check_tx_success(response, "ConfidentialMPTConvertBack")
    client.request(LEDGER_ACCEPT_REQUEST)
    print(f"Converted {convert_back_amount} confidential tokens back to public")


if __name__ == "__main__":
    main()
