from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.requests import Fee, GenericRequest, Request
from xrpl.models.requests.request import _DEFAULT_API_VERSION


class TestRequest(TestCase):
    def test_to_dict_includes_method_as_string(self):
        req = Fee()
        value = req.to_dict()["method"]
        self.assertEqual(type(value), str)

    def test_generic_request_to_dict_sets_command_as_method(self):
        command = "validator_list_sites"
        req = GenericRequest(command=command).to_dict()
        expected = {**req, "api_version": _DEFAULT_API_VERSION}
        self.assertDictEqual(req, expected)

    def test_from_dict(self):
        req = {"method": "account_tx", "account": "rN6zcSynkRnf8zcgTVrRL8K7r4ovE7J4Zj"}
        obj = Request.from_dict(req)
        self.assertEqual(obj.__class__.__name__, "AccountTx")
        expected = {
            **req,
            "binary": False,
            "forward": False,
            "api_version": _DEFAULT_API_VERSION,
        }
        self.assertDictEqual(obj.to_dict(), expected)

    def test_from_dict_no_method(self):
        req = {"account": "rN6zcSynkRnf8zcgTVrRL8K7r4ovE7J4Zj"}
        with self.assertRaises(XRPLModelException):
            Request.from_dict(req)

    def test_from_dict_wrong_method(self):
        req = {"method": "account_tx"}
        with self.assertRaises(XRPLModelException):
            Fee.from_dict(req)

    def test_from_dict_noripple_check(self):
        req = {
            "method": "noripple_check",
            "account": "rN6zcSynkRnf8zcgTVrRL8K7r4ovE7J4Zj",
            "role": "user",
        }
        obj = Request.from_dict(req)
        self.assertEqual(obj.__class__.__name__, "NoRippleCheck")
        expected = {
            **req,
            "transactions": False,
            "limit": 300,
            "api_version": _DEFAULT_API_VERSION,
        }
        self.assertDictEqual(obj.to_dict(), expected)

    def test_from_dict_account_nfts(self):
        req = {
            "method": "account_nfts",
            "account": "rN6zcSynkRnf8zcgTVrRL8K7r4ovE7J4Zj",
        }
        obj = Request.from_dict(req)
        expected = {**req, "api_version": _DEFAULT_API_VERSION}
        self.assertEqual(obj.__class__.__name__, "AccountNFTs")
        self.assertDictEqual(obj.to_dict(), expected)

    def test_from_dict_amm_info(self):
        req = {
            "method": "amm_info",
            "amm_account": "rN6zcSynkRnf8zcgTVrRL8K7r4ovE7J4Zj",
        }
        obj = Request.from_dict(req)
        expected = {**req, "api_version": _DEFAULT_API_VERSION}
        self.assertEqual(obj.__class__.__name__, "AMMInfo")
        self.assertDictEqual(obj.to_dict(), expected)

    def test_from_dict_nft_history(self):
        req = {
            "method": "nft_history",
            "nft_id": "00000000",
        }
        obj = Request.from_dict(req)
        expected = {
            **req,
            "binary": False,
            "forward": False,
            "api_version": _DEFAULT_API_VERSION,
        }
        self.assertEqual(obj.__class__.__name__, "NFTHistory")
        self.assertDictEqual(obj.to_dict(), expected)

    def test_from_dict_generic_request(self):
        req = {
            "method": "tx_history",
            "start": 0,
        }
        obj = Request.from_dict(req)
        expected = {**req, "api_version": _DEFAULT_API_VERSION}
        self.assertEqual(obj.__class__.__name__, "GenericRequest")
        self.assertDictEqual(obj.to_dict(), expected)
