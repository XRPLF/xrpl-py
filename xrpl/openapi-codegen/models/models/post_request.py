from dataclasses import field
from typing import Union
from xrpl.models.requests.request import RequestMethod

POST = Union[SchemasAccountChannelsRequest, SchemasAccountInfoRequest, SchemasAccountLinesRequest, SchemasLedgerEntryRequest, SchemasServerInfoRequest, SchemasSubmitRequestV1]

