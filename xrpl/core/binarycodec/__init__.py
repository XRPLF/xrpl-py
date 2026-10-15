"""
Functions for encoding objects into the XRP Ledger's canonical
binary format and decoding them.
"""

from xrpl.core.binarycodec.exceptions import XRPLBinaryCodecException
from xrpl.core.binarycodec.main import (
    decode,
    encode,
    encode_for_multisigning,
    encode_for_multisigning_counterparty,
    encode_for_multisigning_sponsor,
    encode_for_signing,
    encode_for_signing_batch,
    encode_for_signing_claim,
    encode_for_signing_counterparty,
    encode_for_signing_sponsor,
)

__all__ = [
    "decode",
    "encode",
    "encode_for_signing_batch",
    "encode_for_multisigning",
    "encode_for_multisigning_counterparty",
    "encode_for_multisigning_sponsor",
    "encode_for_signing",
    "encode_for_signing_counterparty",
    "encode_for_signing_sponsor",
    "encode_for_signing_claim",
    "XRPLBinaryCodecException",
]
