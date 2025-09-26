"""Hash Utilities for XRPL Ledger Objects.

This module provides utilities for computing hashes of various XRPL ledger objects.
These functions are essential for Batch transactions where you need to know the hash
of a ledger entry object before it's created on the ledger.

Example:
    >>> from xrpl.utils.hash_utils import hash_offer, hash_escrow
    >>> offer_hash = hash_offer("rAccount...", 123)
    >>> escrow_hash = hash_escrow("rAccount...", 456)
"""

import hashlib
import re
from typing import Union

from xrpl.core import addresscodec

# Constants
BYTE_LENGTH = 4  # 4 bytes for sequence numbers
SEQ_HEX_LEN = BYTE_LENGTH * 2  # 8 hex chars

# Ledger space dictionary mapping ledger object types to their namespace identifiers
LEDGER_SPACES = {
    "account": "a",
    "dirNode": "d",
    "generatorMap": "g",
    "rippleState": "r",
    "offer": "o",
    "ownerDir": "O",
    "bookDir": "B",
    "contract": "c",
    "skipList": "s",
    "escrow": "u",
    "amendment": "f",
    "feeSettings": "e",
    "ticket": "T",
    "signerList": "S",
    "paychan": "x",
    "check": "C",
    "depositPreauth": "p",
}

# Precompute hex (4 chars) once at import time
LEDGER_SPACES_HEX = {k: format(ord(v), "x").zfill(4) for k, v in LEDGER_SPACES.items()}


def sha512_half(data: Union[str, bytes, bytearray, memoryview]) -> str:
    """Compute the SHA-512 hash and then take the first half of the result.

    Args:
        data: The input data in hexadecimal format (str) or bytes-like object.

    Returns:
        The first half of the SHA-512 hash in uppercase hexadecimal.
    
    Raises:
        TypeError: If data is not str or bytes-like.
        ValueError: If hex string is malformed.
    """
    if isinstance(data, (bytes, bytearray, memoryview)):
        buf = bytes(data)
    elif isinstance(data, str):
        buf = bytes.fromhex(data)
    else:
        raise TypeError("data must be hex str or bytes-like")
    
    hash_obj = hashlib.sha512(buf)
    return hash_obj.digest()[:32].hex().upper()


def _u32_hex(n: int) -> str:
    """Convert a 32-bit unsigned integer to 8-character hex string.
    
    Args:
        n: Integer to convert (must be in range [0, 2^32 - 1]).
        
    Returns:
        8-character lowercase hex string with zero padding.
        
    Raises:
        ValueError: If n is outside the valid 32-bit unsigned range.
    """
    if n < 0 or n > 0xFFFFFFFF:
        raise ValueError("u32 sequence out of range (0..=2^32-1)")  # noqa: TRY003
    return f"{n:0{SEQ_HEX_LEN}X}"


def address_to_hex(address: str) -> str:
    """Convert an XRPL address to its hexadecimal representation.

    Args:
        address: The classic XRPL address to convert (starts with 'r').

    Returns:
        The hexadecimal representation of the address.

    Raises:
        XRPLAddressCodecException or ValueError: If the address is invalid.
    """
    return addresscodec.decode_classic_address(address).hex().upper()


def ledger_space_hex(name: str) -> str:
    """Get the hexadecimal representation of a ledger space.

    Args:
        name: The name of the ledger space.

    Returns:
        The hexadecimal representation of the ledger space (4 characters).

    Raises:
        KeyError: If the ledger space name is not recognized.
    """
    return LEDGER_SPACES_HEX[name]


def hash_account_root(address: str) -> str:
    """Compute the hash of an AccountRoot ledger entry.

    Args:
        address: The classic account address.

    Returns:
        The computed hash of the account root in uppercase hexadecimal.
    """
    return sha512_half(ledger_space_hex("account") + address_to_hex(address))


def hash_offer(address: str, sequence: int) -> str:
    """Compute the hash of an Offer ledger entry.

    Args:
        address: The address associated with the offer.
        sequence: The sequence number of the offer transaction.

    Returns:
        The computed hash of the offer in uppercase hexadecimal.
    """
    return sha512_half(
        ledger_space_hex("offer")
        + address_to_hex(address)
        + _u32_hex(sequence)
    )


def hash_check(address: str, sequence: int) -> str:
    """Compute the hash of a Check ledger entry.

    Args:
        address: The address associated with the check.
        sequence: The sequence number of the check transaction.

    Returns:
        The computed hash of the check in uppercase hexadecimal.
    """
    return sha512_half(
        ledger_space_hex("check")
        + address_to_hex(address)
        + _u32_hex(sequence)
    )


def hash_escrow(address: str, sequence: int) -> str:
    """Compute the hash of an Escrow ledger entry.

    Args:
        address: The address associated with the escrow.
        sequence: The sequence number of the escrow transaction.

    Returns:
        The computed hash of the escrow in uppercase hexadecimal.
    """
    return sha512_half(
        ledger_space_hex("escrow")
        + address_to_hex(address)
        + _u32_hex(sequence)
    )


def hash_payment_channel(address: str, dst_address: str, sequence: int) -> str:
    """Compute the hash of a Payment Channel ledger entry.

    Args:
        address: The address of the payment channel creator.
        dst_address: The destination address for the payment channel.
        sequence: The sequence number of the payment channel transaction.

    Returns:
        The computed hash of the payment channel in uppercase hexadecimal.
    """
    return sha512_half(
        ledger_space_hex("paychan")
        + address_to_hex(address)
        + address_to_hex(dst_address)
        + _u32_hex(sequence)
    )


def hash_signer_list_id(address: str) -> str:
    """Compute the hash of a SignerList ledger entry.

    Args:
        address: The classic account address of the SignerList owner.

    Returns:
        The computed hash of the signer list in uppercase hexadecimal.
    """
    return sha512_half(
        ledger_space_hex("signerList") + address_to_hex(address) + _u32_hex(0)
    )


def hash_trustline(address1: str, address2: str, currency: Union[str, bytes]) -> str:
    """Compute the hash of a Trustline (RippleState) ledger entry.

    Args:
        address1: One of the addresses in the trustline.
        address2: The other address in the trustline.
        currency: The currency code (3 characters) or currency hash.

    Returns:
        The computed hash of the trustline in uppercase hexadecimal.
    """
    # Convert addresses to hex
    addr1_hex = address_to_hex(address1)
    addr2_hex = address_to_hex(address2)
    
    # Ensure consistent ordering (lower address first)
    if addr1_hex > addr2_hex:
        addr1_hex, addr2_hex = addr2_hex, addr1_hex
    
    # Handle currency formatting (must be 20 bytes)
    if isinstance(currency, str) and len(currency) == 3:
        # Canonicalize 3-char currency to uppercase
        currency_hex = ("00" * 12) + currency.upper().encode("ascii").hex().upper() + ("00" * 5)
    elif isinstance(currency, bytes):
        if len(currency) != 20:
            raise ValueError("Currency bytes must be exactly 20 bytes.")  # noqa: TRY003
        currency_hex = currency.hex().upper()
    else:
        hex_str = str(currency)
        if not re.fullmatch(r"[0-9A-Fa-f]{40}", hex_str):
            raise ValueError("Currency hex must be exactly 40 hex characters.")  # noqa: TRY003
        currency_hex = hex_str.upper()
    
    return sha512_half(
        ledger_space_hex("rippleState") + addr1_hex + addr2_hex + currency_hex
    )


def hash_ticket(address: str, ticket_sequence: int) -> str:
    """Compute the hash of a Ticket ledger entry.

    Args:
        address: The address associated with the ticket.
        ticket_sequence: The TicketSequence (32-bit) used to derive the Ticket index.

    Returns:
        The computed hash of the ticket in uppercase hexadecimal.
    """
    return sha512_half(
        ledger_space_hex("ticket")
        + address_to_hex(address)
        + _u32_hex(ticket_sequence)
    )


def hash_deposit_preauth(address: str, authorized_address: str) -> str:
    """Compute the hash of a DepositPreauth ledger entry.

    Args:
        address: The account that granted the authorization.
        authorized_address: The account that was authorized.

    Returns:
        The computed hash of the deposit preauth in uppercase hexadecimal.
    """
    return sha512_half(
        ledger_space_hex("depositPreauth")
        + address_to_hex(address)
        + address_to_hex(authorized_address)
    )

# Aliases for compatibility with different naming conventions
hash_offer_id = hash_offer
hash_ripple_state = hash_trustline