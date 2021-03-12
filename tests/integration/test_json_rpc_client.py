import unittest

from xrpl.models.requests.accounts import AccountInfo
from xrpl.network_clients.json_rpc_client import JsonRpcClient

JSON_RPC_URL = "http://test.xrp.xpring.io:51234"

TESTNET_CLASSIC_ADDRESS = "rwW4a42ShNo9N7Etf1x1yf2jpfDWmsb4L9"


class TestJsonRpcClient(unittest.TestCase):
    def test_account_info(self):
        client = JsonRpcClient(JSON_RPC_URL)

        test_account_info_request = AccountInfo(
            account=TESTNET_CLASSIC_ADDRESS,
            ledger_index="current",
            queue=True,
            strict=True,
        )

        response = client.request(test_account_info_request)
        print("response.status: ", response.status)
        print("response.result: ", response.result)
        print("response.id: ", response.id)
        print("response.type: ", response.type)
