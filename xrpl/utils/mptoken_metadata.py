"""Utils to get an XChainClaimID from metadata."""

import json
from typing import Any, Dict, List

from xrpl.models.transactions.mptoken_issuance_create import MPTokenMetadata
from xrpl.models.utils import HEX_REGEX, MAX_MPTOKEN_METADATA_LENGTH
from xrpl.utils.str_conversions import hex_to_str, str_to_hex

MPT_META_WARNING_HEADER = (
    "MPTokenMetadata is not properly formatted as JSON as per the XLS-89d standard. "
    "While adherence to this standard is not mandatory, such non-compliant MPToken's "
    "might not be discoverable by Explorers and Indexers in the XRPL ecosystem."
)

MPT_META_URI_FIELDS = [
    {"long": "uri", "compact": "u"},
    {"long": "category", "compact": "c"},
    {"long": "title", "compact": "t"},
]

MPT_META_ALL_FIELDS = [
    {"long": "ticker", "compact": "t"},
    {"long": "name", "compact": "n"},
    {"long": "icon", "compact": "i"},
    {"long": "asset_class", "compact": "ac"},
    {"long": "issuer_name", "compact": "in"},
    {"long": "desc", "compact": "d"},
    {"long": "asset_subclass", "compact": "as"},
    {"long": "uris", "compact": "us"},
    {"long": "additional_info", "compact": "ai"},
]


def _expand_keys(
    input_dict: Dict[str, Any], mappings: List[Dict[str, str]]
) -> Dict[str, Any]:
    output = {}
    for key, value in input_dict.items():
        mapping = next((m for m in mappings if key in (m["long"], m["compact"])), None)
        if mapping is None:
            output[key] = value
            continue
        if mapping["long"] in input_dict and mapping["compact"] in input_dict:
            output[key] = value
            continue
        output[mapping["long"]] = value
    return output


def _decode_mptoken_metadata(input: str) -> MPTokenMetadata:
    """
    Decodes hex encoded MPTokenMetadata to a JSON object with long field names.
    Converts compact field names back to their long form equivalents.

    @param input - Hex encoded MPTokenMetadata.
    @returns Decoded MPTokenMetadata object with long field names.
    @throws Error if input is not valid hex or cannot be parsed as JSON.
    @category Utilities
    """
    if bool(HEX_REGEX.fullmatch(input)) is False:
        raise ValueError("MPTokenMetadata must be in hex format.")

    try:
        json_metadata = json.loads(hex_to_str(input))
    except Exception as e:
        raise ValueError(
            f"MPTokenMetadata is not properly formatted as JSON - {e}"
        ) from e

    if not isinstance(json_metadata, dict):
        raise ValueError("MPTokenMetadata must be a JSON object.")

    output = _expand_keys(json_metadata, MPT_META_ALL_FIELDS)

    if isinstance(output.get("uris"), list):
        output["uris"] = [
            _expand_keys(u, MPT_META_URI_FIELDS)
            for u in output["uris"]
            if isinstance(u, dict)
        ]
    if isinstance(output.get("us"), list):
        output["us"] = [
            _expand_keys(u, MPT_META_URI_FIELDS)
            for u in output["us"]
            if isinstance(u, dict)
        ]

    return output  # type: ignore


def _shorten_keys(
    input_dict: Dict[str, Any], mappings: List[Dict[str, str]]
) -> Dict[str, Any]:
    output = {}
    for key, value in input_dict.items():
        mapping = next((m for m in mappings if key in (m["long"], m["compact"])), None)

        if mapping is None:
            output[key] = value
            continue

        if mapping["long"] in input_dict and mapping["compact"] in input_dict:
            output[key] = value
            continue

        output[mapping["compact"]] = value
    return output


def _encode_mptoken_metadata(mptoken_metadata: MPTokenMetadata) -> str:
    """
    Encodes MPTokenMetadata object to a hex string.
    Shortens long field names to their compact form along the way.

    @param mptokenMetadata - MPTokenMetadata to encode.
    @returns Hex encoded MPTokenMetadata.
    @throws Error if input is not a JSON object.
    """
    if not isinstance(mptoken_metadata, Dict):
        raise TypeError("MPTokenMetadata must be JSON object.")

    input_dict = _shorten_keys(dict(mptoken_metadata), MPT_META_ALL_FIELDS)

    if isinstance(input_dict.get("uris"), list):
        input_dict["uris"] = [
            _shorten_keys(u, MPT_META_URI_FIELDS)
            for u in input_dict["uris"]
            if isinstance(u, dict)
        ]

    if isinstance(input_dict.get("us"), list):
        input_dict["us"] = [
            _shorten_keys(u, MPT_META_URI_FIELDS)
            for u in input_dict["us"]
            if isinstance(u, dict)
        ]

    return str_to_hex(json.dumps(input_dict, ensure_ascii=False))


def validate_mptoken_metadata(input: str) -> List[str]:
    """
    Validates MPTokenMetadata adheres to XLS-89 standard.

    @param input - Hex encoded MPTokenMetadata.
    @returns Validation messages if MPTokenMetadata does not adheres to XLS-89 standard.
    @category Utilities
    """
    messages = []

    if bool(HEX_REGEX.fullmatch(input)) is False:
        messages.append("MPTokenMetadata must be in hex format.")
        return messages

    if len(input) == 0 or len(input) > MAX_MPTOKEN_METADATA_LENGTH:
        messages.append(
            f"MPTokenMetadata must be max {int(MAX_MPTOKEN_METADATA_LENGTH / 2)} bytes."
        )
        return messages

    try:
        json_metadata = json.loads(hex_to_str(input))
    except Exception as e:
        messages.append(f"MPTokenMetadata is not properly formatted as JSON - {e}")
        return messages

    if not isinstance(json_metadata, dict):
        messages.append(
            "MPTokenMetadata is not properly formatted JSON object as per XLS-89."
        )
        return messages

    if len(json_metadata.keys()) > len(MPT_META_ALL_FIELDS):
        messages.append(
            f"MPTokenMetadata must not contain more than {len(MPT_META_ALL_FIELDS)} top-level fields "
            f"(found {len(json_metadata.keys())})."
        )

    # NOTE: In TypeScript, complex per-field validation exists.
    # This Python version only performs structural validation.
    # You can add additional checks similar to the TS version if needed.

    return messages
