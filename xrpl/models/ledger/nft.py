from typing_extensions import TypedDict


class NFTokenFields(TypedDict):
    NFTokenID: str
    URI: str


class NFToken(TypedDict):
    NFToken: NFTokenFields
