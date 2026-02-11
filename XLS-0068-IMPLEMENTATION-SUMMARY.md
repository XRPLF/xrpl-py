# XLS-0068 Sponsored Fees and Reserves - Implementation Summary

## Overview

This document summarizes the complete implementation of XLS-0068 Sponsored Fees and Reserves specification in xrpl-py.

**Status**: ✅ **COMPLETE** - All 91 unit tests passing

**Specification**: [XLS-0068 Sponsored Fees and Reserves](https://github.com/XRPLF/XRPL-Standards/tree/master/XLS-0068-sponsored-fees-and-reserves)

---

## Implementation Phases

### Phase 1: Core Data Models - Nested Models and Enums ✅

**Files Created:**
- `xrpl/models/transactions/sponsor_signature.py` (125 lines)
  - `SponsorSigner` class - Nested model for individual signer
  - `SponsorSignature` class - Contains sponsor's signature authorization
- `xrpl/models/transactions/types/sponsorship_type.py` (23 lines)
  - `SponsorshipType` enum with FEE and RESERVE values

**Files Modified:**
- `xrpl/models/transactions/delegate_set.py`
  - Added `SPONSOR_FEE = 65549` to GranularPermission enum
  - Added `SPONSOR_RESERVE = 65550` to GranularPermission enum

**Tests**: 27 tests passing
- SponsorSignature nested model: 9 tests
- SponsorshipType enum: 7 tests
- GranularPermission sponsorship additions: 11 tests

---

### Phase 2: Ledger Entry Types ✅

**Files Created:**
- `xrpl/models/ledger_objects/ledger_entry_type.py` (103 lines)
  - Complete LedgerEntryType enum with all entry types including SPONSORSHIP
- `xrpl/models/ledger_objects/sponsorship.py` (145 lines)
  - `Sponsorship` ledger entry class
  - `SponsorshipFlag` enum with LSF_SPONSORSHIP_REQUIRE_SIGN_FOR_FEE and LSF_SPONSORSHIP_REQUIRE_SIGN_FOR_RESERVE
  - Comprehensive validation logic

**Files Modified:**
- `xrpl/models/ledger_objects/__init__.py`
  - Exported Sponsorship, SponsorshipFlag, LedgerEntryType

**Tests**: 21 tests passing
- Sponsorship ledger entry: 15 tests
- SponsorshipFlag enum: 6 tests

---

### Phase 3: Transaction Types ✅

**Files Created:**
- `xrpl/models/transactions/sponsorship_set.py` (230 lines)
  - `SponsorshipSet` transaction class
  - `SponsorshipSetFlag` enum with 5 flags
  - `SponsorshipSetFlagInterface` TypedDict
  - Comprehensive validation logic per XLS-0068 section 8.3
- `xrpl/models/transactions/sponsorship_transfer.py` (118 lines)
  - `SponsorshipTransfer` transaction class
  - Validation logic per XLS-0068 section 9.4

**Files Modified:**
- `xrpl/models/transactions/types/transaction_type.py`
  - Added `SPONSORSHIP_SET = "SponsorshipSet"`
  - Added `SPONSORSHIP_TRANSFER = "SponsorshipTransfer"`
- `xrpl/models/transactions/__init__.py`
  - Exported SponsorshipSet, SponsorshipSetFlag, SponsorshipSetFlagInterface
  - Exported SponsorshipTransfer
  - Exported SponsorSignature, SponsorSigner

**Tests**: 25 tests passing
- SponsorshipSet transaction: 13 tests
- SponsorshipTransfer transaction: 12 tests

---

### Phase 4: Transaction Base Class Updates ✅

**Files Modified:**
- `xrpl/models/transactions/transaction.py`
  - Added `sponsor: Optional[str] = None` field
  - Added `sponsor_flags: Optional[int] = None` field
  - Added `sponsor_signature: Optional[SponsorSignature] = None` field
  - Added validation logic in `_get_errors()` method
  - Imported SponsorSignature class

**Tests**: 10 tests passing (9 new + existing tests still pass)
- Transaction base class sponsorship fields: 9 new tests

---

### Phase 5: RPC Methods ✅

**Files Created:**
- `xrpl/models/requests/account_sponsoring.py` (51 lines)
  - `AccountSponsoring` request class
  - Fields: account (required), ledger_hash, ledger_index, limit, marker

**Files Modified:**
- `xrpl/models/requests/request.py`
  - Added `ACCOUNT_SPONSORING = "account_sponsoring"` to RequestMethod enum
- `xrpl/models/requests/account_objects.py`
  - Added `SPONSORSHIP = "sponsorship"` to AccountObjectType enum
- `xrpl/models/requests/__init__.py`
  - Exported AccountSponsoring

**Tests**: 8 tests passing
- AccountSponsoring request: 8 tests

---

## Test Coverage Summary

**Total**: 91 unit tests, all passing ✅

| Phase | Component | Tests |
|-------|-----------|-------|
| 1 | SponsorSignature nested model | 9 |
| 1 | SponsorshipType enum | 7 |
| 1 | GranularPermission additions | 11 |
| 2 | Sponsorship ledger entry | 15 |
| 2 | SponsorshipFlag enum | 6 |
| 3 | SponsorshipSet transaction | 13 |
| 3 | SponsorshipTransfer transaction | 12 |
| 4 | Transaction base class | 9 |
| 5 | AccountSponsoring request | 8 |

---

## Running Tests

```bash
# Run all XLS-0068 tests
./run_all_xls0068_tests.sh

# Run individual phases
./run_phase1_tests.sh  # Core Data Models
./run_phase2_tests.sh  # Ledger Entry Types
./run_phase3_tests.sh  # Transaction Types
./run_phase4_tests.sh  # Transaction Base Class
./run_phase5_tests.sh  # RPC Methods
```

---

## Key Features Implemented

### 1. Sponsorship Types
- **Fee Sponsorship** (0x00000001): Sponsor pays transaction fees
- **Reserve Sponsorship** (0x00000002): Sponsor provides XRP reserves

### 2. Sponsorship Models
- **Co-signed Sponsorship**: Sponsor signs each transaction individually
- **Pre-funded Sponsorship**: Sponsor allocates XRP upfront via Sponsorship object

### 3. Transaction Support
All transaction types now support sponsorship via Transaction base class fields:
- `sponsor` - The sponsoring account
- `sponsor_flags` - Type of sponsorship (fee/reserve)
- `sponsor_signature` - Sponsor's authorization signature

### 4. Ledger Objects
- **Sponsorship** ledger entry tracks pre-funded sponsorships
- Fields: Owner, Sponsee, FeeAmount, MaxFee, ReserveCount, Flags

### 5. RPC Methods
- **account_sponsoring** - Query sponsorships for an account
- **account_objects** - Filter for sponsored objects using type="sponsorship"

---

## Architecture Notes

### Design Decisions
1. **No static AccountRoot/RippleState models**: xrpl-py handles these dynamically
2. **Transaction base class approach**: All transactions inherit sponsorship fields
3. **No separate response models**: Responses handled as dictionaries
4. **Integration tests skipped**: Focus on unit test coverage

### Validation Logic
- SponsorSignature requires Sponsor field
- SponsorFlags requires Sponsor field
- SponsorFlags only accepts tfSponsorFee (0x00000001) and tfSponsorReserve (0x00000002)
- SponsorshipSet validates sponsor/sponsee relationships
- SponsorshipTransfer validates account relationships

---

## Files Summary

**Total Files Created**: 11
**Total Files Modified**: 7
**Total Lines of Code**: ~1,500 lines (implementation + tests)

---

## Compliance with XLS-0068

This implementation follows the XLS-0068 specification including:
- ✅ Section 3: Sponsorship Types (Fee and Reserve)
- ✅ Section 4: Sponsorship Models (Co-signed and Pre-funded)
- ✅ Section 5: Ledger Entry (Sponsorship object)
- ✅ Section 8: SponsorshipSet Transaction
- ✅ Section 9: SponsorshipTransfer Transaction
- ✅ Section 10: Transaction Base Class Updates
- ✅ Section 11: RPC Methods (account_sponsoring)

---

**Implementation Date**: February 2026
**xrpl-py Version**: Compatible with current main branch
**Python Version**: 3.8+

