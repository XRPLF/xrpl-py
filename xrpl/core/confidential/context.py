"""
Context hash computation for confidential MPT transactions.

This module provides functions to compute transaction context hashes
that match rippled's implementation using the utility layer.

The context hash is a 32-byte value computed as SHA512Half of transaction-specific
data, used to bind zero-knowledge proofs to specific transactions.
"""

from typing import Union

from xrpl.core.addresscodec import decode_classic_address
from xrpl.core.confidential.crypto_bindings import ffi, lib

# Transaction type codes (from rippled)
TX_TYPE_CONFIDENTIAL_CONVERT = 85
TX_TYPE_CONFIDENTIAL_MERGE_INBOX = 86
TX_TYPE_CONFIDENTIAL_CONVERT_BACK = 87
TX_TYPE_CONFIDENTIAL_SEND = 88
TX_TYPE_CONFIDENTIAL_CLAWBACK = 89


def compute_convert_context_hash(
    account: Union[str, bytes],
    sequence: int,
    mpt_issuance_id: Union[str, bytes],
) -> str:
    """
    Compute context hash for ConfidentialMPTConvert transaction using utility layer.

    Args:
        account: Account address (classic address string) or account ID
                 (20 bytes or 40-char hex string)
        sequence: Transaction sequence number
        mpt_issuance_id: 24-byte MPT issuance ID (bytes or 48-char hex string)

    Returns:
        64-char hex string (32-byte context hash)

    Example:
        >>> context = compute_convert_context_hash(
        ...     "rN7n7otQDd6FczFgLdlqtyMVrn3z1oqh3V",
        ...     100,
        ...     "000004A2A67A324B17A366D8F0D768C32B23180D6A1E54B7",
        ... )
    """
    # Convert account to bytes
    if isinstance(account, str):
        try:
            account_id = decode_classic_address(account)
        except (ValueError, KeyError):
            account_id = bytes.fromhex(account)
    else:
        account_id = account

    # Convert mpt_issuance_id to bytes
    if isinstance(mpt_issuance_id, str):
        issuance_id = bytes.fromhex(mpt_issuance_id)
    else:
        issuance_id = mpt_issuance_id

    if len(account_id) != 20:
        raise ValueError("account_id must be 20 bytes")
    if len(issuance_id) != 24:
        raise ValueError("mpt_issuance_id must be 24 bytes")

    # Create account_id struct
    acc = ffi.new("account_id *")
    for i in range(20):
        acc.bytes[i] = account_id[i]

    # Create mpt_issuance_id struct
    issuance = ffi.new("mpt_issuance_id *")
    for i in range(24):
        issuance.bytes[i] = issuance_id[i]

    # Call utility layer function
    out_hash = ffi.new("uint8_t[32]")
    result = lib.mpt_get_convert_context_hash(acc[0], issuance[0], sequence, out_hash)
    if result != 0:
        raise RuntimeError("Failed to compute convert context hash")

    return bytes(out_hash[0:32]).hex().upper()


def compute_convert_back_context_hash(
    account: Union[str, bytes],
    sequence: int,
    mpt_issuance_id: Union[str, bytes],
    version: int,
) -> str:
    """
    Compute context hash for ConfidentialMPTConvertBack transaction using utility layer.

    Args:
        account: Account address (classic address string) or account ID
                 (20 bytes or 40-char hex string)
        sequence: Transaction sequence number
        mpt_issuance_id: 24-byte MPT issuance ID (bytes or 48-char hex string)
        version: ConfidentialBalanceVersion from ledger

    Returns:
        64-char hex string (32-byte context hash)

    Example:
        >>> context = compute_convert_back_context_hash(
        ...     "rN7n7otQDd6FczFgLdlqtyMVrn3z1oqh3V",
        ...     100,
        ...     "000004A2A67A324B17A366D8F0D768C32B23180D6A1E54B7",
        ...     1
        ... )
    """
    # Convert account to bytes
    if isinstance(account, str):
        try:
            account_id = decode_classic_address(account)
        except (ValueError, KeyError):
            account_id = bytes.fromhex(account)
    else:
        account_id = account

    # Convert mpt_issuance_id to bytes
    if isinstance(mpt_issuance_id, str):
        issuance_id = bytes.fromhex(mpt_issuance_id)
    else:
        issuance_id = mpt_issuance_id

    if len(account_id) != 20:
        raise ValueError("account_id must be 20 bytes")
    if len(issuance_id) != 24:
        raise ValueError("mpt_issuance_id must be 24 bytes")

    # Create account_id struct
    acc = ffi.new("account_id *")
    for i in range(20):
        acc.bytes[i] = account_id[i]

    # Create mpt_issuance_id struct
    issuance = ffi.new("mpt_issuance_id *")
    for i in range(24):
        issuance.bytes[i] = issuance_id[i]

    # Call utility layer function
    out_hash = ffi.new("uint8_t[32]")
    result = lib.mpt_get_convert_back_context_hash(
        acc[0], issuance[0], sequence, version, out_hash
    )
    if result != 0:
        raise RuntimeError("Failed to compute convert back context hash")

    return bytes(out_hash[0:32]).hex().upper()


def compute_send_context_hash(
    account: Union[str, bytes],
    sequence: int,
    mpt_issuance_id: Union[str, bytes],
    destination: Union[str, bytes],
    version: int,
) -> str:
    """
    Compute context hash for ConfidentialMPTSend transaction using utility layer.

    Note: Version is the sender's ConfidentialBalanceVersion, NOT the amount!

    Args:
        account: Sender address (classic address string) or account ID
                 (20 bytes or 40-char hex string)
        sequence: Transaction sequence number
        mpt_issuance_id: 24-byte MPT issuance ID (bytes or 48-char hex string)
        destination: Receiver address (classic address string) or account ID
                     (20 bytes or 40-char hex string)
        version: Sender's ConfidentialBalanceVersion from ledger

    Returns:
        64-char hex string (32-byte context hash)

    Example:
        >>> context = compute_send_context_hash(
        ...     "rN7n7otQDd6FczFgLdlqtyMVrn3z1oqh3V",
        ...     100,
        ...     "000004A2A67A324B17A366D8F0D768C32B23180D6A1E54B7",
        ...     "rPEPPER7kfTD9w2To4CQk6UCfuHM9c6GDY",
        ...     1
        ... )
    """
    # Convert account to bytes
    if isinstance(account, str):
        # Try to decode as classic address first, otherwise treat as hex
        try:
            account_id = decode_classic_address(account)
        except (ValueError, KeyError):
            account_id = bytes.fromhex(account)
    else:
        account_id = account

    # Convert destination to bytes
    if isinstance(destination, str):
        # Try to decode as classic address first, otherwise treat as hex
        try:
            dest_id = decode_classic_address(destination)
        except (ValueError, KeyError):
            dest_id = bytes.fromhex(destination)
    else:
        dest_id = destination

    # Convert mpt_issuance_id to bytes
    if isinstance(mpt_issuance_id, str):
        issuance_id = bytes.fromhex(mpt_issuance_id)
    else:
        issuance_id = mpt_issuance_id

    if len(account_id) != 20:
        raise ValueError("account_id must be 20 bytes")
    if len(dest_id) != 20:
        raise ValueError("destination must be 20 bytes")
    if len(issuance_id) != 24:
        raise ValueError("mpt_issuance_id must be 24 bytes")

    # Create account_id struct
    acc = ffi.new("account_id *")
    for i in range(20):
        acc.bytes[i] = account_id[i]

    # Create destination account_id struct
    dest = ffi.new("account_id *")
    for i in range(20):
        dest.bytes[i] = dest_id[i]

    # Create mpt_issuance_id struct
    issuance = ffi.new("mpt_issuance_id *")
    for i in range(24):
        issuance.bytes[i] = issuance_id[i]

    # Call utility layer function
    out_hash = ffi.new("uint8_t[32]")
    result = lib.mpt_get_send_context_hash(
        acc[0], issuance[0], sequence, dest[0], version, out_hash
    )
    if result != 0:
        raise RuntimeError("Failed to compute send context hash")

    return bytes(out_hash[0:32]).hex().upper()


def compute_clawback_context_hash(
    issuer: Union[str, bytes],
    sequence: int,
    mpt_issuance_id: Union[str, bytes],
    holder: Union[str, bytes],
) -> str:
    """
    Compute context hash for ConfidentialMPTClawback transaction using utility layer.

    Args:
        issuer: Issuer address (classic address string) or account ID
                (20 bytes or 40-char hex string)
        sequence: Transaction sequence number
        mpt_issuance_id: 24-byte MPT issuance ID (bytes or 48-char hex string)
        holder: Holder address (classic address string) or account ID
                (20 bytes or 40-char hex string)

    Returns:
        64-char hex string (32-byte context hash)

    Example:
        >>> context = compute_clawback_context_hash(
        ...     "rN7n7otQDd6FczFgLdlqtyMVrn3z1oqh3V",
        ...     100,
        ...     "000004A2A67A324B17A366D8F0D768C32B23180D6A1E54B7",
        ...     "rPEPPER7kfTD9w2To4CQk6UCfuHM9c6GDY"
        ... )
    """
    # Convert issuer to bytes
    if isinstance(issuer, str):
        # Try to decode as classic address first, otherwise treat as hex
        try:
            issuer_id = decode_classic_address(issuer)
        except (ValueError, KeyError):
            issuer_id = bytes.fromhex(issuer)
    else:
        issuer_id = issuer

    # Convert holder to bytes
    if isinstance(holder, str):
        # Try to decode as classic address first, otherwise treat as hex
        try:
            holder_id = decode_classic_address(holder)
        except (ValueError, KeyError):
            holder_id = bytes.fromhex(holder)
    else:
        holder_id = holder

    # Convert mpt_issuance_id to bytes
    if isinstance(mpt_issuance_id, str):
        issuance_id = bytes.fromhex(mpt_issuance_id)
    else:
        issuance_id = mpt_issuance_id

    if len(issuer_id) != 20:
        raise ValueError("issuer_id must be 20 bytes")
    if len(holder_id) != 20:
        raise ValueError("holder_id must be 20 bytes")
    if len(issuance_id) != 24:
        raise ValueError("mpt_issuance_id must be 24 bytes")

    # Create issuer account_id struct
    iss = ffi.new("account_id *")
    for i in range(20):
        iss.bytes[i] = issuer_id[i]

    # Create holder account_id struct
    hold = ffi.new("account_id *")
    for i in range(20):
        hold.bytes[i] = holder_id[i]

    # Create mpt_issuance_id struct
    issuance = ffi.new("mpt_issuance_id *")
    for i in range(24):
        issuance.bytes[i] = issuance_id[i]

    # Call utility layer function
    out_hash = ffi.new("uint8_t[32]")
    result = lib.mpt_get_clawback_context_hash(
        iss[0], issuance[0], sequence, hold[0], out_hash
    )
    if result != 0:
        raise RuntimeError("Failed to compute clawback context hash")

    return bytes(out_hash[0:32]).hex().upper()
