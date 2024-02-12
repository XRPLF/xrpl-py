from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.requests import Tx

_TRANSACTION_HASH = "C53ECF838647FA5A4C780377025FEC7999AB4182590510CA461444B207AB74A9"
_CTID = "C005523E00000000"


class TestTx(TestCase):
    def test_invalid_input_ctid_and_txn_hash(self):
        with self.assertRaises(XRPLModelException):
            Tx(transaction=_TRANSACTION_HASH, ctid=_CTID)

    # Note: This test merely verifies the semantic correctness of the Request.
    # It does not verify if the specified CTID exists.
    def test_valid_ctid(self):
        request = Tx(ctid=_CTID)
        self.assertTrue(request.is_valid())

    def test_valid_txn_hash(self):
        request = Tx(transaction=_TRANSACTION_HASH)
        self.assertTrue(request.is_valid())
