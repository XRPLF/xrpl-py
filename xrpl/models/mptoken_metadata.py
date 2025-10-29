"""Models for MPTokenMetadata as per the XLS-89 standard."""

from typing import Any, Dict, List, Optional, TypedDict, Union


class MPTokenMetadataUri(TypedDict, total=False):
    """
    MPTokenMetadataUri object as per the XLS-89 standard.
    Represents a URI entry in the MPTokenMetadata using long-form field names.
    Used within the `uris` array of {@link MPTokenMetadata}.
    """

    uri: str
    """
    URI to the related resource.
    Can be a `hostname/path` (HTTPS assumed)
    or full URI for other protocols (e.g., ipfs://).

    @example "exampleyield.com/tbill" or "ipfs://QmXxxx"
    """

    category: str
    """
    The category of the link.
    Allowed values: "website", "social", "docs", "other"

    @example "website"
    """

    title: str
    """
    A human-readable label for the link.
    Any UTF-8 string.

    @example "Product Page"
    """


class MPTokenMetadata(TypedDict, total=False):
    """
    MPTokenMetadata object as per the XLS-89 standard.
    Represents metadata for a Multi-Purpose Token using long-form field names.
    This format is more human-readable and is recommended for client-side usage.
    Use {@link encodeMPTokenMetadata} utility function to convert to a compact hex string for on-ledger storage.
    Use {@link decodeMPTokenMetadata} utility function to convert from a hex string to this format.
    """

    ticker: str
    """
    Ticker symbol used to represent the token.
    Uppercase letters (A-Z) and digits (0-9) only. Max 6 characters recommended.

    @example "TBILL"
    """

    name: str
    """
    Display name of the token.
    Any UTF-8 string.

    @example "T-Bill Yield Token"
    """

    icon: str
    """
    URI to the token icon.
    Can be a `hostname/path` (HTTPS assumed) or full URI for other protocols (e.g., ipfs://).

    @example "example.org/token-icon.png" or "ipfs://QmXxxx"
    """

    asset_class: str
    """
    Top-level classification of token purpose.
    Allowed values: "rwa", "memes", "wrapped", "gaming", "defi", "other"

    @example "rwa"
    """

    issuer_name: str
    """
    The name of the issuer account.
    Any UTF-8 string.

    @example "Example Yield Co."
    """

    desc: Optional[str]
    """
    Short description of the token.
    Any UTF-8 string.

    @example "A yield-bearing stablecoin backed by short-term U.S. Treasuries"
    """

    asset_subclass: Optional[str]
    """
    Optional subcategory of the asset class.
    Required if `asset_class` is "rwa".
    Allowed values: "stablecoin", "commodity", "real_estate",
    "private_credit", "equity", "treasury", "other"

    @example "treasury"
    """

    uris: Optional[List[MPTokenMetadataUri]]
    """
    List of related URIs (site, dashboard, social media, documentation, etc.).
    Each URI object contains the link, its category, and a human-readable title.
    """

    additional_info: Optional[Union[str, Dict[str, Any]]]
    """
    Freeform field for key token details like interest rate,
    maturity date, term, or other relevant info.
    Can be any valid JSON object or UTF-8 string.

    @example { "interest_rate": "5.00%", "maturity_date": "2045-06-30" }
    """
