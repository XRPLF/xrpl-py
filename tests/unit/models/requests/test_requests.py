from unittest import TestCase

from xrpl.models.requests import Fee, SubmitOnly
from xrpl.models.requests.request import Request


class TestRequest(TestCase):
    def test_to_dict_includes_method_as_string(self):
        tx = Fee()
        value = tx.to_dict()["method"]
        self.assertEqual(type(value), str)

    def test_from_dict(self):
        value = {"method": "fee", "id": "request_fee_0"}
        request = Request.from_dict(value)
        self.assertTrue(isinstance(request, Fee))
        self.assertEqual(request.method.value, value["method"])

    def test_from_dict_submit(self):
        req_id = "request_submit_2"
        tx_blob = "12001522000000002401068F922E00000003201B01068FAB6840000000"
        value = {"method": "submit", "tx_blob": tx_blob, "id": req_id}
        expected = SubmitOnly(tx_blob=tx_blob, id=req_id)
        request = Request.from_dict(value)
        self.assertEqual(request, expected)
