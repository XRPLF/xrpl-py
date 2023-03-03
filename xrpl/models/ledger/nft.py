from typing import TypedDict


class NFTokenFields(TypedDict):
    NFTokenId: str
    URI: str

class NFToken(TypedDict):
    NFToken: NFTokenFields