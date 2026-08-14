#!/usr/bin/env python3
"""
XLS-0068 Sponsored Fees and Reserves - Quick Demo

This demo showcases the key features of the XLS-0068 implementation in xrpl-py.
It demonstrates creating sponsored transactions, sponsorship objects, and queries.
"""

from xrpl.models.transactions import (
    Payment,
    SponsorshipSet,
    SponsorshipTransfer,
    SponsorSignature,
)
from xrpl.models.ledger_objects import Sponsorship, SponsorshipFlag
from xrpl.models.requests import AccountSponsoring, AccountObjects, AccountObjectType
from xrpl.models.transactions.types import SponsorshipType


def demo_sponsored_payment():
    """Demo 1: Create a Payment transaction with fee sponsorship."""
    print("=" * 70)
    print("DEMO 1: Sponsored Payment Transaction")
    print("=" * 70)
    
    # Create a payment with a sponsor paying the fee
    payment = Payment(
        account="rSender1234567890123456789012345",
        destination="rReceiver123456789012345678901",
        amount="1000000",  # 1 XRP
        sponsor="rSponsor123456789012345678901234",
        sponsor_flags=0x00000001,  # tfSponsorFee
        sponsor_signature=SponsorSignature(
            signing_pub_key="0330E7FC9D56BB25D6893BA3F317AE5BCF33B3291BD63DB32654A313222F7FD020",
            txn_signature="3045022100D184EB4AE5956FF600E7536EE459345C7BBCF097A84CC61A93B9AF7197EDB98702201CEA8009B7BEEBAA2AACC0359B41C427C1C5B550A4CA4B80CF2174AF2D6D5DCE",
        ),
    )
    
    print(f"\n✅ Created sponsored payment:")
    print(f"   Sender: {payment.account}")
    print(f"   Destination: {payment.destination}")
    print(f"   Amount: {payment.amount}")
    print(f"   Sponsor: {payment.sponsor}")
    print(f"   Sponsor Flags: {hex(payment.sponsor_flags)}")
    print(f"   Valid: {payment.is_valid()}")
    
    # Show the transaction as dict
    print(f"\n📄 Transaction as dict:")
    tx_dict = payment.to_dict()
    for key in ['Account', 'Destination', 'Amount', 'Sponsor', 'SponsorFlags']:
        if key in tx_dict:
            print(f"   {key}: {tx_dict[key]}")
    
    return payment


def demo_sponsorship_set():
    """Demo 2: Create a SponsorshipSet transaction for pre-funded sponsorship."""
    print("\n" + "=" * 70)
    print("DEMO 2: SponsorshipSet Transaction (Pre-funded Sponsorship)")
    print("=" * 70)
    
    # Sponsor creates a pre-funded sponsorship for a sponsee
    sponsorship_set = SponsorshipSet(
        account="rSponsor123456789012345678901234",
        sponsee="rSponsee123456789012345678901234",
        fee_amount="10000000",  # 10 XRP for fees
        max_fee="100",  # Max 100 drops per transaction
        reserve_count=5,  # Sponsor 5 reserves
    )
    
    print(f"\n✅ Created SponsorshipSet:")
    print(f"   Sponsor (Account): {sponsorship_set.account}")
    print(f"   Sponsee: {sponsorship_set.sponsee}")
    print(f"   Fee Amount: {sponsorship_set.fee_amount} drops")
    print(f"   Max Fee per Tx: {sponsorship_set.max_fee} drops")
    print(f"   Reserve Count: {sponsorship_set.reserve_count}")
    print(f"   Valid: {sponsorship_set.is_valid()}")
    
    return sponsorship_set


def demo_sponsorship_transfer():
    """Demo 3: Transfer sponsorship to a new sponsor."""
    print("\n" + "=" * 70)
    print("DEMO 3: SponsorshipTransfer Transaction")
    print("=" * 70)
    
    # Transfer sponsorship from current sponsor to new sponsor
    transfer = SponsorshipTransfer(
        account="rSponsor123456789012345678901234",
        sponsee="rSponsee123456789012345678901234",
        new_sponsor="rNewSponsor1234567890123456789",
    )
    
    print(f"\n✅ Created SponsorshipTransfer:")
    print(f"   Current Sponsor: {transfer.account}")
    print(f"   Sponsee: {transfer.sponsee}")
    print(f"   New Sponsor: {transfer.new_sponsor}")
    print(f"   Valid: {transfer.is_valid()}")
    
    return transfer


def demo_sponsorship_ledger_entry():
    """Demo 4: Create a Sponsorship ledger entry."""
    print("\n" + "=" * 70)
    print("DEMO 4: Sponsorship Ledger Entry")
    print("=" * 70)
    
    # Create a sponsorship ledger entry
    sponsorship = Sponsorship(
        owner="rSponsor123456789012345678901234",
        sponsee="rSponsee123456789012345678901234",
        fee_amount="5000000",  # 5 XRP
        max_fee="50",
        reserve_count=3,
        flags=SponsorshipFlag.LSF_SPONSORSHIP_REQUIRE_SIGN_FOR_FEE,
    )
    
    print(f"\n✅ Created Sponsorship ledger entry:")
    print(f"   Owner (Sponsor): {sponsorship.owner}")
    print(f"   Sponsee: {sponsorship.sponsee}")
    print(f"   Fee Amount: {sponsorship.fee_amount} drops")
    print(f"   Max Fee: {sponsorship.max_fee} drops")
    print(f"   Reserve Count: {sponsorship.reserve_count}")
    print(f"   Flags: {hex(sponsorship.flags)}")
    print(f"   Valid: {sponsorship.is_valid()}")
    
    return sponsorship


def demo_account_sponsoring_request():
    """Demo 5: Query sponsorships for an account."""
    print("\n" + "=" * 70)
    print("DEMO 5: AccountSponsoring RPC Request")
    print("=" * 70)
    
    # Create a request to query all sponsorships for an account
    request = AccountSponsoring(
        account="rSponsor123456789012345678901234",
        ledger_index="validated",
        limit=10,
    )
    
    print(f"\n✅ Created AccountSponsoring request:")
    print(f"   Account: {request.account}")
    print(f"   Ledger Index: {request.ledger_index}")
    print(f"   Limit: {request.limit}")
    print(f"   Method: {request.method}")
    print(f"   Valid: {request.is_valid()}")
    
    # Show request as dict (ready to send to rippled)
    print(f"\n📄 Request as dict:")
    req_dict = request.to_dict()
    for key, value in req_dict.items():
        print(f"   {key}: {value}")
    
    return request


def demo_account_objects_filter():
    """Demo 6: Filter for sponsored objects using AccountObjects."""
    print("\n" + "=" * 70)
    print("DEMO 6: AccountObjects with Sponsorship Filter")
    print("=" * 70)
    
    # Query account objects filtered by sponsorship type
    request = AccountObjects(
        account="rSponsor123456789012345678901234",
        type=AccountObjectType.SPONSORSHIP,
        ledger_index="validated",
    )
    
    print(f"\n✅ Created AccountObjects request:")
    print(f"   Account: {request.account}")
    print(f"   Type Filter: {request.type}")
    print(f"   Ledger Index: {request.ledger_index}")
    print(f"   Valid: {request.is_valid()}")
    
    return request


def main():
    """Run all demos."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  XLS-0068 Sponsored Fees and Reserves - Demo".center(68) + "║")
    print("║" + "  xrpl-py Implementation".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    
    # Run all demos
    demo_sponsored_payment()
    demo_sponsorship_set()
    demo_sponsorship_transfer()
    demo_sponsorship_ledger_entry()
    demo_account_sponsoring_request()
    demo_account_objects_filter()
    
    # Summary
    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print("\n✅ All XLS-0068 features demonstrated successfully!")
    print("\nKey Features:")
    print("  • Sponsored transactions (co-signed model)")
    print("  • Pre-funded sponsorships (SponsorshipSet)")
    print("  • Sponsorship transfers (SponsorshipTransfer)")
    print("  • Sponsorship ledger entries")
    print("  • RPC queries (AccountSponsoring, AccountObjects)")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()

