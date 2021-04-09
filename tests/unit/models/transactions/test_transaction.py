from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import OfferCreate
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types.transaction_type import TransactionType

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_FEE = "0.00001"
_SEQUENCE = 19048


class TestTransaction(TestCase):
    def test_missing_required_field(self):
        with self.assertRaises(XRPLModelException):
            # missing account
            Transaction(
                fee=_FEE,
                sequence=_SEQUENCE,
                transaction_type=TransactionType.ACCOUNT_DELETE,
            )

    def test_initializes_if_all_required_fields_present(self):
        tx = Transaction(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            transaction_type=TransactionType.ACCOUNT_DELETE,
        )
        self.assertTrue(tx.is_valid())

    def test_to_dict_includes_type_as_string(self):
        tx = Transaction(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            transaction_type=TransactionType.ACCOUNT_DELETE,
        )
        value = tx.to_dict()["transaction_type"]
        self.assertEqual(type(value), str)

    def test_get_hash(self):
        offer_create_dict = {
            "Account": "rLyttXLh7Ttca9CMUaD3exVoXY2fn2zwj3",
            "Fee": "10",
            "Flags": 0,
            "LastLedgerSequence": 16409087,
            "Sequence": 16409064,
            "SigningPubKey": (
                "ED93BFA583E83331E9DC498DE4558CE4861ACFAB9385EBBC43BC56A0D9845A1DF2"
            ),
            "TakerGets": "13100000",
            "TakerPays": {
                "currency": "USD",
                "issuer": "rLyttXLh7Ttca9CMUaD3exVoXY2fn2zwj3",
                "value": "10",
            },
            "TransactionType": "OfferCreate",
            "TxnSignature": (
                "71135999783658A0CB4EBCF02E59ACD94C4D06D5BF909E05E6B97588155482BBA5985"
                "35AD4728ACA1F90C4DE73FFC741B0A6AB87141BDA8BCC2F2DF9CD8C3703"
            ),
        }

        offer_create = OfferCreate.from_xrpl(offer_create_dict)
        expected_hash = (
            "66F3D6158CAB6E53405F8C264DB39F07D8D0454433A63DDFB98218ED1BC99B60"
        )
        self.assertEqual(offer_create.get_hash(), expected_hash)

    def test_to_dict_flag_list(self):
        tx = Transaction(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            transaction_type=TransactionType.ACCOUNT_DELETE,
            flags=[0b1, 0b10, 0b100],
        )
        expected_flags = 0b111
        value = tx.to_dict()["flags"]
        self.assertEqual(value, expected_flags)
