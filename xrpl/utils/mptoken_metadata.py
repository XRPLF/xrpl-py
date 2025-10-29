"""Utility functions for encoding, decoding and validating MPTokenMetadata."""

import json
import re
from typing import Any, Dict, List

from typing_extensions import Final, Pattern

from xrpl.models.mptoken_metadata import MPTokenMetadata
from xrpl.utils.str_conversions import hex_to_str, str_to_hex

HEX_REGEX: Final[Pattern[str]] = re.compile("[a-fA-F0-9]*")

MAX_MPTOKEN_METADATA_LENGTH = 1024 * 2

MPT_META_ASSET_CLASSES = [
    "rwa",
    "memes",
    "wrapped",
    "gaming",
    "defi",
    "other",
]

MPT_META_ASSET_SUB_CLASSES = [
    "stablecoin",
    "commodity",
    "real_estate",
    "private_credit",
    "equity",
    "treasury",
    "other",
]

MPT_META_WARNING_HEADER = (
    "MPTokenMetadata is not properly formatted as JSON as per the XLS-89d standard. "
    "While adherence to this standard is not mandatory, such non-compliant MPToken's "
    "might not be discoverable by Explorers and Indexers in the XRPL ecosystem."
)


def _validate_ticker(obj: Dict[str, Any]) -> List[str]:
    if "ticker" in obj and "t" in obj:
        return ["ticker/t: both long and compact forms present. expected only one."]
    value = obj.get("ticker") if "ticker" in obj else obj.get("t")
    if not isinstance(value, str) or not re.compile(r"^[A-Z0-9]{1,6}$").match(value):
        return [
            "ticker/t: should have uppercase letters (A-Z) and digits (0-9) "
            "only. Max 6 characters recommended."
        ]
    return []


def _validate_name(obj: Dict[str, Any]) -> List[str]:
    if "name" in obj and "n" in obj:
        return ["name/n: both long and compact forms present. expected only one."]
    value = obj.get("name") if "name" in obj else obj.get("n")
    if not isinstance(value, str) or len(value) == 0:
        return ["name/n: should be a non-empty string."]
    return []


def _validate_icon(obj: Dict[str, Any]) -> List[str]:
    if "icon" in obj and "i" in obj:
        return ["icon/i: both long and compact forms present. expected only one."]
    value = obj.get("icon") if "icon" in obj else obj.get("i")
    if not isinstance(value, str) or len(value) == 0:
        return ["icon/i: should be a non-empty string."]
    return []


def _validate_asset_class(obj: Dict[str, Any]) -> List[str]:
    if "asset_class" in obj and "ac" in obj:
        return [
            "asset_class/ac: both long and compact forms present. expected only one."
        ]
    value = obj.get("asset_class") if "asset_class" in obj else obj.get("ac")
    if not isinstance(value, str) or value not in MPT_META_ASSET_CLASSES:
        return [
            f"asset_class/ac: should be one of {', '.join(MPT_META_ASSET_CLASSES)}."
        ]
    return []


def _validate_issuer_name(obj: Dict[str, Any]) -> List[str]:
    if "issuer_name" in obj and "in" in obj:
        return [
            "issuer_name/in: both long and compact forms present. expected only one."
        ]
    value = obj.get("issuer_name") if "issuer_name" in obj else obj.get("in")
    if not isinstance(value, str) or len(value) == 0:
        return ["issuer_name/in: should be a non-empty string."]
    return []


def _validate_desc(obj: Dict[str, Any]) -> List[str]:
    if "desc" in obj and "d" in obj:
        return ["desc/d: both long and compact forms present. expected only one."]
    # optional: if both undefined -> ok
    if "desc" not in obj and "d" not in obj:
        return []
    value = obj.get("desc") if "desc" in obj else obj.get("d")
    if not isinstance(value, str) or len(value) == 0:
        return ["desc/d: should be a non-empty string."]
    return []


def _validate_asset_subclass(obj: Dict[str, Any]) -> List[str]:
    if "asset_subclass" in obj and "as" in obj:
        return [
            "asset_subclass/as: both long and compact forms present. expected only one."
        ]
    value = obj.get("asset_subclass") if "asset_subclass" in obj else obj.get("as")
    # required if asset_class is rwa (consider both long and compact asset_class)
    asset_class_val = obj.get("asset_class") if "asset_class" in obj else obj.get("ac")
    if (asset_class_val == "rwa") and (value is None):
        return ["asset_subclass/as: required when asset_class is rwa."]
    # if both undefined -> ok
    if "asset_subclass" not in obj and "as" not in obj:
        return []
    if not isinstance(value, str) or value not in MPT_META_ASSET_SUB_CLASSES:
        return [
            "asset_subclass/as: should be one of "
            f"{', '.join(MPT_META_ASSET_SUB_CLASSES)}."
        ]
    return []


def _validate_uris(obj: Dict[str, Any]) -> List[str]:
    if "uris" in obj and "us" in obj:
        return ["uris/us: both long and compact forms present. expected only one."]
    if "uris" not in obj and "us" not in obj:
        return []
    value = obj.get("uris") if "uris" in obj else obj.get("us")
    if not isinstance(value, list) or len(value) == 0:
        return ["uris/us: should be a non-empty array."]
    messages: List[str] = []
    for uri_obj in value:
        if not isinstance(uri_obj, Dict) or len(list(uri_obj.keys())) != len(
            MPT_META_URI_FIELDS
        ):
            messages.append(
                "uris/us: should be an array of objects each with uri/u, "
                "category/c, and title/t properties."
            )
            continue
        uri = uri_obj.get("uri") if "uri" in uri_obj else uri_obj.get("u")
        category = (
            uri_obj.get("category") if "category" in uri_obj else uri_obj.get("c")
        )
        title = uri_obj.get("title") if "title" in uri_obj else uri_obj.get("t")
        if (
            not isinstance(uri, str)
            or not isinstance(category, str)
            or not isinstance(title, str)
        ):
            messages.append(
                "uris/us: should be an array of objects each with uri/u, "
                "category/c, and title/t properties."
            )
    return messages


def _validate_additional_info(obj: Dict[str, Any]) -> List[str]:
    if "additional_info" in obj and "ai" in obj:
        return [
            "additional_info/ai: both long and compact forms present. "
            "expected only one."
        ]
    if "additional_info" not in obj and "ai" not in obj:
        return []
    value = obj.get("additional_info") if "additional_info" in obj else obj.get("ai")
    if not isinstance(value, str) or isinstance(value, Dict):
        return ["additional_info/ai: should be a string or JSON object."]
    return []


MPT_META_URI_FIELDS = [
    {"long": "uri", "compact": "u"},
    {"long": "category", "compact": "c"},
    {"long": "title", "compact": "t"},
]

MPT_META_ALL_FIELDS = [
    {"long": "ticker", "compact": "t", "validate": _validate_ticker},
    {"long": "name", "compact": "n", "validate": _validate_name},
    {"long": "icon", "compact": "i", "validate": _validate_icon},
    {"long": "asset_class", "compact": "ac", "validate": _validate_asset_class},
    {"long": "issuer_name", "compact": "in", "validate": _validate_issuer_name},
    {"long": "desc", "compact": "d", "validate": _validate_desc},
    {
        "long": "asset_subclass",
        "compact": "as",
        "validate": _validate_asset_subclass,
    },
    {"long": "uris", "compact": "us", "validate": _validate_uris},
    {
        "long": "additional_info",
        "compact": "ai",
        "validate": _validate_additional_info,
    },
]


def _expand_keys(
    input_dict: Dict[str, Any], mappings: List[Dict[str, Any]]
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


def decode_mptoken_metadata(input_hex: str) -> MPTokenMetadata:
    """
    Decodes hex encoded MPTokenMetadata to a JSON object with long field names.
    Converts compact field names back to their long form equivalents.

    @param input - Hex encoded MPTokenMetadata.
    @returns Decoded MPTokenMetadata object with long field names.
    @throws Error if input is not valid hex or cannot be parsed as JSON.
    @category Utilities
    """
    if bool(HEX_REGEX.fullmatch(input_hex)) is False:
        raise ValueError("MPTokenMetadata must be in hex format.")

    try:
        json_metadata = json.loads(hex_to_str(input_hex))
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
    input_dict: Dict[str, Any], mappings: List[Dict[str, Any]]
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


def encode_mptoken_metadata(mptoken_metadata: MPTokenMetadata) -> str:
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

    return str_to_hex(json.dumps(input_dict, ensure_ascii=False, sort_keys=True))


def validate_mptoken_metadata(input_hex: str) -> List[str]:
    """
    Validates if MPTokenMetadata adheres to XLS-89d standard.

    Args:
        input_hex (str): Hex encoded MPTokenMetadata.

    Returns:
        List[str]: A list of validation error messages.
    """
    validation_messages: List[str] = []

    if bool(HEX_REGEX.fullmatch(input_hex)) is False:
        validation_messages.append("MPTokenMetadata must be in hex format.")
        return validation_messages

    if len(input_hex) == 0 or len(input_hex) > MAX_MPTOKEN_METADATA_LENGTH:
        validation_messages.append(
            (
                "MPTokenMetadata must be non-empty and max "
                f"{int(MAX_MPTOKEN_METADATA_LENGTH / 2)} bytes."
            )
        )
        return validation_messages

    try:
        decoded_str = hex_to_str(input_hex)
        json_metadata = json.loads(decoded_str)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        validation_messages.append(
            f"MPTokenMetadata is not properly formatted as JSON - {str(e)}"
        )
        return validation_messages

    if not isinstance(json_metadata, Dict):
        validation_messages.append(
            "MPTokenMetadata is not properly formatted JSON object as per XLS-89."
        )
        return validation_messages

    # Structure validation

    field_count = len(json_metadata.keys())
    if field_count > len(MPT_META_ALL_FIELDS):
        validation_messages.append(
            (
                "MPTokenMetadata must not contain more than "
                f"{len(MPT_META_ALL_FIELDS)} top-level fields "
                f"(found {field_count})."
            )
        )
        return validation_messages

    obj = json_metadata

    # Run per-field validators in same order as TS
    for prop in MPT_META_ALL_FIELDS:
        validate_fn = prop.get("validate")
        if callable(validate_fn):
            validation_messages.extend(validate_fn(obj))

    return validation_messages
