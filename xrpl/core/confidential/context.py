"""
Context hash computation for confidential MPT transactions.

This module provides functions to compute transaction context hashes
that match rippled's implementation. These are used with the C bindings
approach (mpt_crypto_bindings) rather than the charm-crypto approach.

The context hash is a 32-byte value computed as SHA512Half of transaction-specific
data, used to bind zero-knowledge proofs to specific transactions.
"""

import hashlib
import struct
from typing import Union

from xrpl.core.addresscodec import decode_classic_address

# Transaction type codes (from rippled)
TX_TYPE_CONFIDENTIAL_CONVERT = 85
TX_TYPE_CONFIDENTIAL_MERGE_INBOX = 86
TX_TYPE_CONFIDENTIAL_CONVERT_BACK = 87
TX_TYPE_CONFIDENTIAL_SEND = 88
TX_TYPE_CONFIDENTIAL_CLAWBACK = 89


def compute_convert_context_hash(
    account: Union[str, bytes],
    sequence: int,
    mpt_issuance_id: bytes,
    amount: int,
) -> bytes:
    """
    Compute context hash for ConfidentialMPTConvert transaction.

    Format: TX_TYPE (2) + Account (20) + Sequence (4) + IssuanceID (24) + Amount (8)
    Total: 58 bytes → SHA512Half

    Args:
        account: Account address (string) or account ID (20 bytes)
        sequence: Transaction sequence number
        mpt_issuance_id: 24-byte MPT issuance ID
        amount: Amount to convert (uint64)

    Returns:
        32-byte context hash

    Example:
        >>> context = compute_convert_context_hash(
        ...     "rN7n7otQDd6FczFgLdlqtyMVrn3z1oqh3V",
        ...     100,
        ...     bytes.fromhex("000004A2A67A324B17A366D8F0D768C32B23180D6A1E54B7"),
        ...     1000
        ... )
    """
    account_id = (
        decode_classic_address(account) if isinstance(account, str) else account
    )

    context_bytes = struct.pack(">H", TX_TYPE_CONFIDENTIAL_CONVERT)
    context_bytes += account_id
    context_bytes += struct.pack(">I", sequence)
    context_bytes += mpt_issuance_id
    context_bytes += struct.pack(">Q", amount)

    return hashlib.sha512(context_bytes).digest()[:32]


def compute_convert_back_context_hash(
    account: Union[str, bytes],
    sequence: int,
    mpt_issuance_id: bytes,
    amount: int,
    version: int,
) -> bytes:
    """
    Compute context hash for ConfidentialMPTConvertBack transaction.

    Format: TX_TYPE (2) + Account (20) + Sequence (4) + IssuanceID (24)
            + Amount (8) + Version (4)
    Total: 62 bytes → SHA512Half

    Args:
        account: Account address (string) or account ID (20 bytes)
        sequence: Transaction sequence number
        mpt_issuance_id: 24-byte MPT issuance ID
        amount: Amount to convert back (uint64)
        version: ConfidentialBalanceVersion from ledger

    Returns:
        32-byte context hash

    Example:
        >>> context = compute_convert_back_context_hash(
        ...     "rN7n7otQDd6FczFgLdlqtyMVrn3z1oqh3V",
        ...     100,
        ...     bytes.fromhex("000004A2A67A324B17A366D8F0D768C32B23180D6A1E54B7"),
        ...     500,
        ...     1
        ... )
    """
    account_id = (
        decode_classic_address(account) if isinstance(account, str) else account
    )

    context_bytes = struct.pack(">H", TX_TYPE_CONFIDENTIAL_CONVERT_BACK)
    context_bytes += account_id
    context_bytes += struct.pack(">I", sequence)
    context_bytes += mpt_issuance_id
    context_bytes += struct.pack(">Q", amount)
    context_bytes += struct.pack(">I", version)

    return hashlib.sha512(context_bytes).digest()[:32]


def compute_send_context_hash(
    account: Union[str, bytes],
    sequence: int,
    mpt_issuance_id: bytes,
    destination: Union[str, bytes],
    version: int,
) -> bytes:
    """
    Compute context hash for ConfidentialMPTSend transaction.

    Format: TX_TYPE (2) + Account (20) + Sequence (4) + IssuanceID (24)
            + Destination (20) + Version (4)
    Total: 74 bytes → SHA512Half

    Note: Version is the sender's ConfidentialBalanceVersion, NOT the amount!

    Args:
        account: Sender address (string) or account ID (20 bytes)
        sequence: Transaction sequence number
        mpt_issuance_id: 24-byte MPT issuance ID
        destination: Receiver address (string) or account ID (20 bytes)
        version: Sender's ConfidentialBalanceVersion from ledger

    Returns:
        32-byte context hash

    Example:
        >>> context = compute_send_context_hash(
        ...     "rN7n7otQDd6FczFgLdlqtyMVrn3z1oqh3V",
        ...     100,
        ...     bytes.fromhex("000004A2A67A324B17A366D8F0D768C32B23180D6A1E54B7"),
        ...     "rPEPPER7kfTD9w2To4CQk6UCfuHM9c6GDY",
        ...     1
        ... )
    """
    account_id = (
        decode_classic_address(account) if isinstance(account, str) else account
    )
    dest_id = (
        decode_classic_address(destination)
        if isinstance(destination, str)
        else destination
    )

    context_bytes = struct.pack(">H", TX_TYPE_CONFIDENTIAL_SEND)
    context_bytes += account_id
    context_bytes += struct.pack(">I", sequence)
    context_bytes += mpt_issuance_id
    context_bytes += dest_id
    context_bytes += struct.pack(">I", version)

    return hashlib.sha512(context_bytes).digest()[:32]


def compute_clawback_context_hash(
    issuer: Union[str, bytes],
    sequence: int,
    mpt_issuance_id: bytes,
    amount: int,
    holder: Union[str, bytes],
) -> bytes:
    """
    Compute context hash for ConfidentialMPTClawback transaction.

    Format: TX_TYPE (2) + Account (20) + Sequence (4) + IssuanceID (24)
            + Amount (8) + Holder (20)
    Total: 78 bytes → SHA512Half

    Args:
        issuer: Issuer address (string) or account ID (20 bytes)
        sequence: Transaction sequence number
        mpt_issuance_id: 24-byte MPT issuance ID
        amount: Amount to claw back (uint64)
        holder: Holder address (string) or account ID (20 bytes)

    Returns:
        32-byte context hash

    Example:
        >>> context = compute_clawback_context_hash(
        ...     "rN7n7otQDd6FczFgLdlqtyMVrn3z1oqh3V",
        ...     100,
        ...     bytes.fromhex("000004A2A67A324B17A366D8F0D768C32B23180D6A1E54B7"),
        ...     500,
        ...     "rPEPPER7kfTD9w2To4CQk6UCfuHM9c6GDY"
        ... )
    """
    issuer_id = decode_classic_address(issuer) if isinstance(issuer, str) else issuer
    holder_id = decode_classic_address(holder) if isinstance(holder, str) else holder

    context_bytes = struct.pack(">H", TX_TYPE_CONFIDENTIAL_CLAWBACK)
    context_bytes += issuer_id
    context_bytes += struct.pack(">I", sequence)
    context_bytes += mpt_issuance_id
    context_bytes += struct.pack(">Q", amount)
    context_bytes += holder_id

    return hashlib.sha512(context_bytes).digest()[:32]
