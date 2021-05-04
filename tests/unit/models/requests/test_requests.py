from unittest import TestCase

from xrpl.models.requests import Fee
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
