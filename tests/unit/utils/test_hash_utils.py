"""Tests for hash utilities."""

from unittest import TestCase

from xrpl.core.addresscodec.exceptions import XRPLAddressCodecException
from xrpl.utils.hash_utils import (
    LEDGER_SPACES,
    address_to_hex,
    hash_account_root,
    hash_check,
    hash_deposit_preauth,
    hash_escrow,
    hash_offer,
    hash_offer_id,
    hash_payment_channel,
    hash_ripple_state,
    hash_signer_list_id,
    hash_ticket,
    hash_trustline,
    ledger_space_hex,
    sha512_half,
)


class TestHashUtilsBasic(TestCase):
    """Test basic hash utility functions."""

    def test_sha512_half(self):
        """Test SHA512 half hash function."""
        # Test with known input/output for "Hello World"
        test_data = "48656C6C6F20576F726C64"  # "Hello World" in hex
        result = sha512_half(test_data)
        # Known SHA-512 half result for "Hello World"
        expected = "2C74FD17EDAFD80E8447B0D46741EE243B7EB74DD2149A0AB1B9246FB30382F2"
        self.assertEqual(result, expected)
        # Should be 64 characters (32 bytes) uppercase hex
        self.assertEqual(len(result), 64)
        self.assertTrue(result.isupper())
        self.assertTrue(all(c in "0123456789ABCDEF" for c in result))
        
        # Test with bytes input
        result_bytes = sha512_half(b"Hello World")
        self.assertEqual(len(result_bytes), 64)
        self.assertTrue(result_bytes.isupper())
        
        # Invalid hex should raise
        with self.assertRaises(ValueError):
            sha512_half("ZZ")  # non-hex
        with self.assertRaises(ValueError):
            sha512_half("A")   # odd length
        
        # Invalid type should raise
        with self.assertRaises(TypeError):
            sha512_half(123)

    def test_address_to_hex(self):
        """Test address to hex conversion."""
        address = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
        result = address_to_hex(address)
        # Should be 40 characters (20 bytes) hex
        self.assertEqual(len(result), 40)
        # Should be valid hex and uppercase
        self.assertTrue(all(c in "0123456789ABCDEF" for c in result))

    def test_address_to_hex_invalid(self):
        """Test address to hex conversion with invalid address."""
        with self.assertRaises((XRPLAddressCodecException, ValueError)):
            address_to_hex("invalid_address")

    def test_ledger_space_hex(self):
        """Test ledger space hex conversion."""
        # Test known ledger spaces
        self.assertEqual(ledger_space_hex("account"), "0061")  # 'a' = 0x61
        self.assertEqual(ledger_space_hex("offer"), "006f")    # 'o' = 0x6f
        self.assertEqual(ledger_space_hex("escrow"), "0075")   # 'u' = 0x75
        self.assertEqual(ledger_space_hex("check"), "0043")    # 'C' = 0x43
        self.assertEqual(ledger_space_hex("paychan"), "0078")  # 'x' = 0x78

    def test_ledger_space_hex_invalid(self):
        """Test ledger space hex with invalid space."""
        with self.assertRaises(KeyError):
            ledger_space_hex("invalid_space")


class TestHashFunctions(TestCase):
    """Test individual hash functions with known test vectors from xrpl.js."""

    def test_hash_account_root(self):
        """Test account root hash calculation."""
        # Test vector from xrpl.js tests
        address = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
        expected = "2B6AC232AA4C4BE41BF49D2459FA4A0347E1B543A4C92FCEE0821C0201E2E9A8"
        result = hash_account_root(address)
        self.assertEqual(result, expected)

    def test_hash_offer(self):
        """Test offer hash calculation."""
        # Test with a simple case first
        address = "r32UufnaCGL82HubijgJGDmdE5hac7ZvLw"
        sequence = 137
        result = hash_offer(address, sequence)
        # Should return a 64-character uppercase hex string
        self.assertEqual(len(result), 64)
        self.assertTrue(result.isupper())
        self.assertTrue(all(c in "0123456789ABCDEF" for c in result))

    def test_hash_offer_alias(self):
        """Test that hash_offer_id is an alias for hash_offer."""
        address = "r32UufnaCGL82HubijgJGDmdE5hac7ZvLw"
        sequence = 137
        self.assertEqual(hash_offer(address, sequence), hash_offer_id(address, sequence))

    def test_hash_signer_list_id(self):
        """Test signer list ID hash calculation."""
        # Test vector from xrpl.js tests
        address = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
        expected = "778365D5180F5DF3016817D1F318527AD7410D83F8636CF48C43E8AF72AB49BF"
        result = hash_signer_list_id(address)
        self.assertEqual(result, expected)

    def test_hash_escrow(self):
        """Test escrow hash calculation."""
        # Test with valid addresses
        address = "rDx69ebzbowuqztksVDmZXjizTd12BVr4x"
        sequence = 84
        result = hash_escrow(address, sequence)
        # Should return a 64-character uppercase hex string
        self.assertEqual(len(result), 64)
        self.assertTrue(result.isupper())
        self.assertTrue(all(c in "0123456789ABCDEF" for c in result))

    def test_hash_payment_channel(self):
        """Test payment channel hash calculation."""
        # Test with valid addresses
        address = "rDx69ebzbowuqztksVDmZXjizTd12BVr4x"
        dst_address = "rLFtVprxUEfsH54eCWKsZrEQzMDsx1wqso"
        sequence = 82
        result = hash_payment_channel(address, dst_address, sequence)
        # Should return a 64-character uppercase hex string
        self.assertEqual(len(result), 64)
        self.assertTrue(result.isupper())
        self.assertTrue(all(c in "0123456789ABCDEF" for c in result))

    def test_hash_trustline(self):
        """Test trustline hash calculation."""
        # Test vector from xrpl.js tests
        address1 = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
        address2 = "rB5TihdPbKgMrkFqrqUC3yLdE8hhv4BdeY"
        currency = "USD"
        expected = "C683B5BB928F025F1E860D9D69D6C554C2202DE0D45877ADB3077DA4CB9E125C"
        result = hash_trustline(address1, address2, currency)
        self.assertEqual(result, expected)

    def test_hash_trustline_ordering(self):
        """Test that trustline hash is consistent regardless of address order."""
        address1 = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
        address2 = "rB5TihdPbKgMrkFqrqUC3yLdE8hhv4BdeY"
        currency = "USD"
        
        # Should produce same hash regardless of order
        result1 = hash_trustline(address1, address2, currency)
        result2 = hash_trustline(address2, address1, currency)
        self.assertEqual(result1, result2)

    def test_hash_trustline_alias(self):
        """Test that hash_ripple_state is an alias for hash_trustline."""
        address1 = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
        address2 = "rB5TihdPbKgMrkFqrqUC3yLdE8hhv4BdeY"
        currency = "USD"
        self.assertEqual(
            hash_trustline(address1, address2, currency),
            hash_ripple_state(address1, address2, currency),
        )

    def test_hash_check(self):
        """Test check hash calculation."""
        # Use a valid XRPL address
        address = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
        sequence = 1
        result = hash_check(address, sequence)
        # Should return a 64-character uppercase hex string
        self.assertEqual(len(result), 64)
        self.assertTrue(result.isupper())
        self.assertTrue(all(c in "0123456789ABCDEF" for c in result))

    def test_hash_ticket(self):
        """Test ticket hash calculation."""
        # Use a valid XRPL address
        address = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
        ticket_id = 25
        result = hash_ticket(address, ticket_id)
        # Should return a 64-character uppercase hex string
        self.assertEqual(len(result), 64)
        self.assertTrue(result.isupper())
        self.assertTrue(all(c in "0123456789ABCDEF" for c in result))

    def test_hash_deposit_preauth(self):
        """Test deposit preauth hash calculation."""
        # Use valid XRPL addresses
        address = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
        authorized_address = "rDx69ebzbowuqztksVDmZXjizTd12BVr4x"
        result = hash_deposit_preauth(address, authorized_address)
        # Should return a 64-character uppercase hex string
        self.assertEqual(len(result), 64)
        self.assertTrue(result.isupper())
        self.assertTrue(all(c in "0123456789ABCDEF" for c in result))

    def test_hash_deposit_preauth_directionality(self):
        """Test that deposit preauth hash is directional."""
        # Use valid XRPL addresses
        address = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
        authorized_address = "rDx69ebzbowuqztksVDmZXjizTd12BVr4x"
        
        # Swapping addresses should produce different hashes
        result1 = hash_deposit_preauth(address, authorized_address)
        result2 = hash_deposit_preauth(authorized_address, address)
        self.assertNotEqual(result1, result2)


class TestEdgeCases(TestCase):
    """Test edge cases and error conditions."""

    def test_sequence_zero(self):
        """Test hash functions with sequence number 0."""
        address = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"

        # These should all work with sequence 0
        result_offer = hash_offer(address, 0)
        self.assertEqual(len(result_offer), 64)

        result_escrow = hash_escrow(address, 0)
        self.assertEqual(len(result_escrow), 64)

        result_check = hash_check(address, 0)
        self.assertEqual(len(result_check), 64)

    def test_large_sequence_number(self):
        """Test hash functions with large sequence numbers."""
        address = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
        large_sequence = 2**32 - 1  # Maximum 32-bit unsigned integer

        result = hash_offer(address, large_sequence)
        self.assertEqual(len(result), 64)
        self.assertTrue(result.isupper())

    def test_invalid_sequence_numbers(self):
        """Test hash functions with invalid sequence numbers."""
        address = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
        
        # Test negative sequence number
        with self.assertRaises(ValueError) as context:
            hash_offer(address, -1)
        self.assertIn("u32 sequence out of range", str(context.exception))
        
        # Test sequence number too large (> 2^32 - 1)
        with self.assertRaises(ValueError) as context:
            hash_offer(address, 2**32)
        self.assertIn("u32 sequence out of range", str(context.exception))
        
        # Test with other hash functions that use sequences
        with self.assertRaises(ValueError):
            hash_escrow(address, -1)
            
        with self.assertRaises(ValueError):
            hash_check(address, 2**32)
            
        with self.assertRaises(ValueError):
            hash_ticket(address, -5)

    def test_invalid_address_in_hash_functions(self):
        """Test hash functions with invalid addresses."""
        invalid_address = "invalid_address"

        with self.assertRaises((XRPLAddressCodecException, ValueError)):
            hash_account_root(invalid_address)

        with self.assertRaises((XRPLAddressCodecException, ValueError)):
            hash_offer(invalid_address, 123)

        with self.assertRaises((XRPLAddressCodecException, ValueError)):
            hash_escrow(invalid_address, 123)

        with self.assertRaises((XRPLAddressCodecException, ValueError)):
            hash_payment_channel(invalid_address, "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh", 1)

        with self.assertRaises((XRPLAddressCodecException, ValueError)):
            hash_payment_channel("rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh", invalid_address, 1)

        with self.assertRaises((XRPLAddressCodecException, ValueError)):
            hash_deposit_preauth(invalid_address, "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh")

        with self.assertRaises((XRPLAddressCodecException, ValueError)):
            hash_deposit_preauth("rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh", invalid_address)

        with self.assertRaises((XRPLAddressCodecException, ValueError)):
            hash_check(invalid_address, 1)

        with self.assertRaises((XRPLAddressCodecException, ValueError)):
            hash_ticket(invalid_address, 1)

    def test_currency_formats(self):
        """Test different currency formats in trustline hash."""
        address1 = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
        address2 = "rB5TihdPbKgMrkFqrqUC3yLdE8hhv4BdeY"
        
        # Standard 3-character currency
        result_usd = hash_trustline(address1, address2, "USD")
        self.assertEqual(len(result_usd), 64)
        
        # Different currency
        result_eur = hash_trustline(address1, address2, "EUR")
        self.assertEqual(len(result_eur), 64)
        self.assertNotEqual(result_usd, result_eur)
        
        # Test case-sensitivity for 3-character currencies (should be different)
        result_usd_lower = hash_trustline(address1, address2, "usd")
        result_usd_mixed = hash_trustline(address1, address2, "UsD")
        self.assertNotEqual(result_usd, result_usd_lower)
        self.assertNotEqual(result_usd, result_usd_mixed)
        self.assertNotEqual(result_usd_lower, result_usd_mixed)
        
        # Test currency as bytes (covers the bytes case) - must be exactly 20 bytes
        currency_bytes = b"USD" + b"\x00" * 17  # 20 bytes total
        result_bytes = hash_trustline(address1, address2, currency_bytes)
        self.assertEqual(len(result_bytes), 64)
        self.assertTrue(result_bytes.isupper())
        
        # Test currency as hex string (covers the else case for non-3-char strings)
        currency_hex = "0000000000000000555344000000000000000000"  # USD as hex, 40 chars
        result_hex = hash_trustline(address1, address2, currency_hex)
        self.assertEqual(len(result_hex), 64)
        self.assertTrue(result_hex.isupper())

    def test_invalid_currency_formats(self):
        """Test invalid currency formats in trustline hash."""
        address1 = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
        address2 = "rB5TihdPbKgMrkFqrqUC3yLdE8hhv4BdeY"
        
        # Test invalid bytes length
        with self.assertRaises(ValueError) as context:
            hash_trustline(address1, address2, b"USD")  # Only 3 bytes, need 20
        self.assertIn("Currency bytes must be exactly 20 bytes", str(context.exception))
        
        # Test invalid hex string length
        with self.assertRaises(ValueError) as context:
            hash_trustline(address1, address2, "INVALID")  # Not 40 hex chars
        self.assertIn("Currency hex must be exactly 40 hex characters", str(context.exception))
        
        # Test invalid hex characters
        with self.assertRaises(ValueError) as context:
            hash_trustline(address1, address2, "ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ")  # 40 chars but invalid hex
        self.assertIn("Currency hex must be exactly 40 hex characters", str(context.exception))

    def test_ledger_spaces_completeness(self):
        """Test that all expected ledger spaces are defined."""
        expected_spaces = [
            "account", "dirNode", "generatorMap", "rippleState", "offer",
            "ownerDir", "bookDir", "contract", "skipList", "escrow",
            "amendment", "feeSettings", "ticket", "signerList", "paychan",
            "check", "depositPreauth"
        ]
        
        for space in expected_spaces:
            self.assertIn(space, LEDGER_SPACES)
            # Should be able to get hex for each space
            hex_result = ledger_space_hex(space)
            self.assertEqual(len(hex_result), 4)
            self.assertTrue(all(c in "0123456789abcdef" for c in hex_result.lower()))

    def test_hash_consistency(self):
        """Test that hash functions produce consistent results."""
        address = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
        
        # Same input should produce same output
        result1 = hash_account_root(address)
        result2 = hash_account_root(address)
        self.assertEqual(result1, result2)
        
        # Same offer parameters should produce same hash
        offer1 = hash_offer(address, 123)
        offer2 = hash_offer(address, 123)
        self.assertEqual(offer1, offer2)
        
        # Different sequence should produce different hash
        offer3 = hash_offer(address, 124)
        self.assertNotEqual(offer1, offer3)

    def test_sequence_formatting(self):
        """Test that sequence numbers are formatted correctly."""
        address = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
        
        # Test small sequence number
        result_small = hash_offer(address, 1)
        self.assertEqual(len(result_small), 64)
        
        # Test larger sequence number
        result_large = hash_offer(address, 1000000)
        self.assertEqual(len(result_large), 64)
        
        # Results should be different
        self.assertNotEqual(result_small, result_large)