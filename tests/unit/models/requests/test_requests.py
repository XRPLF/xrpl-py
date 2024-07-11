from unittest import TestCase

from xrpl.models.requests import Fee, GenericRequest, Request


class TestRequest(TestCase):
    def test_to_dict_includes_method_as_string(self):
        req = Fee()
        value = req.to_dict()["method"]
        self.assertEqual(type(value), str)

    def test_generic_request_to_dict_sets_command_as_method(self):
        command = "validator_list_sites"
        req = GenericRequest(command=command).to_dict()
        self.assertDictEqual(req, {"method": command})

    def test_from_dict(self):
        req = {"method": "account_tx", "account": "rN6zcSynkRnf8zcgTVrRL8K7r4ovE7J4Zj"}
        obj = Request.from_dict(req)
        self.assertEqual(obj.__class__.__name__, "AccountTx")
        expected = {**req, "binary": False, "forward": False}
        self.assertDictEqual(obj.to_dict(), expected)

    def test_from_dict_noripple_check(self):
        req = {
            "method": "noripple_check",
            "account": "rN6zcSynkRnf8zcgTVrRL8K7r4ovE7J4Zj",
            "role": "user",
        }
        obj = Request.from_dict(req)
        self.assertEqual(obj.__class__.__name__, "NoRippleCheck")
        expected = {**req, "transactions": False, "limit": 300}
        self.assertDictEqual(obj.to_dict(), expected)

    def test_from_dict_account_nfts(self):
        req = {
            "method": "account_nfts",
            "account": "rN6zcSynkRnf8zcgTVrRL8K7r4ovE7J4Zj",
        }
        obj = Request.from_dict(req)
        self.assertEqual(obj.__class__.__name__, "AccountNFTs")
        expected = {**req}
        self.assertDictEqual(obj.to_dict(), expected)

    def test_from_dict_amm_info(self):
        req = {
            "method": "amm_info",
            "amm_account": "rN6zcSynkRnf8zcgTVrRL8K7r4ovE7J4Zj",
        }
        obj = Request.from_dict(req)
        self.assertEqual(obj.__class__.__name__, "AMMInfo")
        expected = {**req}
        self.assertDictEqual(obj.to_dict(), expected)
