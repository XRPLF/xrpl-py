"""MPTokenMetadata and MPTokenMetadataUri objects as per the XLS-89 standard."""

from typing import Any, Dict, List, Optional, TypedDict, Union


class MPTokenMetadataUri(TypedDict, total=False):
    """
    MPTokenMetadataUri object as per the XLS-89 standard.

    Used within the `uris` array of MPTokenMetadata object.
    """

    uri: str
    """
    URI to the related resource.

    Can be a ``hostname/path`` (HTTPS assumed) or
    full URI for other protocols (e.g., ipfs://).

    :meta:
        - **Example (Hostname)**: "exampleyield.com/tbill"
        - **Example (Full URI)**: "ipfs://QmXxxx"
    """

    category: str
    """
    The category of the link.

    :Allowed values:
        - "website"
        - "social"
        - "docs"
        - "other"

    :meta:
        - **Example**: "website"
    """

    title: str
    """
    A human-readable label for the link.

    Any UTF-8 string is allowed.

    :meta:
        - **Example**: "Product Page"
    """


class MPTokenMetadata(TypedDict, total=False):
    """
    MPTokenMetadata object as per the XLS-89 standard.

    Use `encode_mptoken_metadata` to convert this object to a compact hex
    string for on-ledger storage.
    Use `decode_mptoken_metadata` to convert from a hex string to this format.
    """

    ticker: str
    """
    Ticker symbol used to represent the token.

    Uppercase letters (A-Z) and digits (0-9) only. Max 6 characters recommended.

    :meta:
        - **Example**: "TBILL"
    """

    name: str
    """
    Display name of the token.

    Any UTF-8 string is allowed.

    :meta:
        - **Example**: "T-Bill Yield Token"
    """

    desc: Optional[str]
    """
    Short description of the token.

    Any UTF-8 string is allowed.

    :meta:
        - **Example**: "A yield-bearing stablecoin backed by short-term U.S. Treasuries"
    """

    icon: str
    """
    URI to the token icon.
    Can be a `hostname/path` (HTTPS assumed) or full URI for other protocols
    (e.g., ipfs://).

    @example "example.org/token-icon.png" or "ipfs://QmXxxx"
    """

    asset_class: str
    """
    Top-level classification of token purpose.

    :Allowed values:
        - "rwa"
        - "memes"
        - "wrapped"
        - "gaming"
        - "defi"
        - "other"

    :meta:
        - **Example**: "rwa"
    """

    asset_subclass: Optional[str]
    """
    Optional subcategory of the asset class.

    Required if the ``asset_class`` field is set to "rwa".

    :Allowed values:
        - "stablecoin"
        - "commodity"
        - "real_estate"
        - "private_credit"
        - "equity"
        - "treasury"
        - "other"

    :meta:
        - **Example**: "treasury"
    """

    issuer_name: str
    """
    The name of the issuer account.

    Any UTF-8 string is allowed.

    :meta:
        - **Example**: "Example Yield Co."
    """

    uris: Optional[List[MPTokenMetadataUri]]
    """
    List of related URIs (site, dashboard, social media, documentation, etc.).

    Each URI object contains the following:
    * The link itself (the URI)
    * Its category (e.g., "website", "docs")
    * A human-readable title
    """

    additional_info: Optional[Union[str, Dict[str, Any]]]
    """
    Freeform field for key token details like interest rate, maturity date,
    term, or other relevant info.

    Can be any valid JSON object or UTF-8 string.

    :meta:
        - **Example**: { "interest_rate": "5.00%", "maturity_date": "2045-06-30" }
    """
