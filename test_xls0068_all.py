#!/usr/bin/env python3
"""
Combined Test Suite for XLS-0068 Sponsored Fees and Reserves Implementation

This test file imports and runs all unit tests from the XLS-0068 implementation.
It provides a single entry point to run all 91 tests across all 5 phases.

Test Coverage:
- Phase 1: Core Data Models (27 tests)
  - SponsorSignature nested model (9 tests)
  - SponsorshipType enum (7 tests)
  - GranularPermission additions (11 tests)

- Phase 2: Ledger Entry Types (21 tests)
  - Sponsorship ledger entry (15 tests)
  - SponsorshipFlag enum (6 tests)

- Phase 3: Transaction Types (25 tests)
  - SponsorshipSet transaction (13 tests)
  - SponsorshipTransfer transaction (12 tests)

- Phase 4: Transaction Base Class Updates (10 tests)
  - Transaction sponsorship fields (9 tests)
  - Existing tests still pass (1 test)

- Phase 5: RPC Methods (8 tests)
  - AccountSponsoring request (8 tests)

Total: 91 unit tests

Usage:
    python3 -m unittest test_xls0068_all -v
    python3 test_xls0068_all.py
"""

import sys
import unittest

# Phase 1: Core Data Models
from tests.unit.models.transactions.test_sponsor_signature import (
    TestSponsorSigner,
    TestSponsorSignature,
)
from tests.unit.models.transactions.types.test_sponsorship_type import (
    TestSponsorshipType,
)
from tests.unit.models.transactions.test_granular_permission_sponsorship import (
    TestGranularPermissionSponsorship,
)

# Phase 2: Ledger Entry Types
from tests.unit.models.ledger_objects.test_sponsorship import (
    TestSponsorship,
    TestSponsorshipFlag,
    TestLedgerEntryType,
)

# Phase 3: Transaction Types
from tests.unit.models.transactions.test_sponsorship_set import TestSponsorshipSet
from tests.unit.models.transactions.test_sponsorship_transfer import (
    TestSponsorshipTransfer,
)

# Phase 4: Transaction Base Class Updates
# Note: We only import the new sponsorship-related tests from test_transaction.py
# The full test_transaction.py file contains many other tests
from tests.unit.models.transactions.test_transaction import TestTransaction

# Phase 5: RPC Methods
from tests.unit.models.requests.test_account_sponsoring import TestAccountSponsoring


def create_test_suite():
    """Create a test suite containing all XLS-0068 tests."""
    suite = unittest.TestSuite()

    # Phase 1: Core Data Models (27 tests)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSponsorSigner))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSponsorSignature))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSponsorshipType))
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestGranularPermissionSponsorship)
    )

    # Phase 2: Ledger Entry Types (21 tests)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSponsorship))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSponsorshipFlag))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLedgerEntryType))

    # Phase 3: Transaction Types (25 tests)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSponsorshipSet))
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestSponsorshipTransfer)
    )

    # Phase 4: Transaction Base Class Updates (10 tests)
    # Load only the sponsorship-related tests from TestTransaction
    loader = unittest.TestLoader()
    transaction_tests = loader.loadTestsFromTestCase(TestTransaction)
    sponsorship_tests = unittest.TestSuite()
    for test in transaction_tests:
        test_method = test._testMethodName
        if "sponsor" in test_method.lower():
            sponsorship_tests.addTest(test)
    suite.addTests(sponsorship_tests)

    # Phase 5: RPC Methods (8 tests)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAccountSponsoring))

    return suite


def print_summary():
    """Print a summary of the test suite."""
    print("=" * 70)
    print("XLS-0068 Sponsored Fees and Reserves - Combined Test Suite")
    print("=" * 70)
    print()
    print("Test Coverage:")
    print("  Phase 1: Core Data Models (27 tests)")
    print("    - SponsorSignature nested model (9 tests)")
    print("    - SponsorshipType enum (7 tests)")
    print("    - GranularPermission additions (11 tests)")
    print()
    print("  Phase 2: Ledger Entry Types (21 tests)")
    print("    - Sponsorship ledger entry (15 tests)")
    print("    - SponsorshipFlag enum (6 tests)")
    print()
    print("  Phase 3: Transaction Types (25 tests)")
    print("    - SponsorshipSet transaction (13 tests)")
    print("    - SponsorshipTransfer transaction (12 tests)")
    print()
    print("  Phase 4: Transaction Base Class Updates (10 tests)")
    print("    - Transaction sponsorship fields (9 tests)")
    print()
    print("  Phase 5: RPC Methods (8 tests)")
    print("    - AccountSponsoring request (8 tests)")
    print()
    print("  Total: 91 unit tests")
    print("=" * 70)
    print()


def main():
    """Run all XLS-0068 tests."""
    print_summary()

    # Create and run the test suite
    suite = create_test_suite()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print final summary
    print()
    print("=" * 70)
    if result.wasSuccessful():
        print("✅ ALL XLS-0068 TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED")
        print(f"   Failures: {len(result.failures)}")
        print(f"   Errors: {len(result.errors)}")
    print("=" * 70)

    # Return appropriate exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())

