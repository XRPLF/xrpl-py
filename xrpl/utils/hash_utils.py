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
from typing import Union

from xrpl.core import addresscodec
from xrpl.utils.str_conversions import str_to_hex

# Constants
HEX = 16
BYTE_LENGTH = 4  # 4 bytes for sequence numbers

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
    "uriToken": "U",
    "depositPreauth": "p",
}


def sha512_half(data: str) -> str:
    """Compute the SHA-512 hash and then take the first half of the result.

    Args:
        data: The input data in hexadecimal format.

    Returns:
        The first half of the SHA-512 hash in uppercase hexadecimal.
    """
    hash_obj = hashlib.sha512(bytes.fromhex(data))
    return hash_obj.hexdigest()[:64].upper()


def address_to_hex(address: str) -> str:
    """Convert an XRPL address to its hexadecimal representation.

    Args:
        address: The classic XRPL address to convert (starts with 'r').

    Returns:
        The hexadecimal representation of the address.

    Raises:
        XRPLAddressCodecException: If the address is invalid.
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
    return format(ord(LEDGER_SPACES[name]), "x").zfill(4)


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
        + format(sequence, "x").zfill(8)  # 4 bytes = 8 hex characters
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
        + format(sequence, "x").zfill(8)  # 4 bytes = 8 hex characters
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
        + format(sequence, "x").zfill(8)  # 4 bytes = 8 hex characters
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
        + format(sequence, "x").zfill(8)  # 4 bytes = 8 hex characters
    )


def hash_signer_list_id(address: str) -> str:
    """Compute the hash of a SignerList ledger entry.

    Args:
        address: The classic account address of the SignerList owner.

    Returns:
        The computed hash of the signer list in uppercase hexadecimal.
    """
    return sha512_half(
        ledger_space_hex("signerList") + address_to_hex(address) + "00000000"
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
    if int(addr1_hex, 16) > int(addr2_hex, 16):
        addr1_hex, addr2_hex = addr2_hex, addr1_hex
    
    # Handle currency formatting
    if isinstance(currency, str) and len(currency) == 3:
        # Standard 3-character currency code
        currency_hex = "00" * 12 + currency.encode('ascii').hex().upper() + "00" * 5
    else:
        # Assume it's already a hex string or bytes
        if isinstance(currency, bytes):
            currency_hex = currency.hex().upper()
        else:
            currency_hex = str(currency).upper()
    
    return sha512_half(
        ledger_space_hex("rippleState") + addr1_hex + addr2_hex + currency_hex
    )


def hash_ticket(address: str, ticket_id: int) -> str:
    """Compute the hash of a Ticket ledger entry.

    Args:
        address: The address associated with the ticket.
        ticket_id: The ticket identifier.

    Returns:
        The computed hash of the ticket in uppercase hexadecimal.
    """
    return sha512_half(
        ledger_space_hex("ticket")
        + address_to_hex(address)
        + format(ticket_id, "x").zfill(8)  # 4 bytes = 8 hex characters
    )


def hash_uri_token(issuer: str, uri: str) -> str:
    """Compute the hash of a URIToken ledger entry.

    This is primarily used in Xahau networks but included for compatibility.

    Args:
        issuer: The address of the issuer.
        uri: The URI associated with the token.

    Returns:
        The computed hash of the URI token in uppercase hexadecimal.
    """
    return sha512_half(
        ledger_space_hex("uriToken") + address_to_hex(issuer) + str_to_hex(uri)
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