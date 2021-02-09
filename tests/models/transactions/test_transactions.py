import unittest

from xrpl.models.transactions.offer_create_transaction import OfferCreateTransaction


class TestOfferCreateTransaction(unittest.TestCase):
    def test_init_to_json(self):
        account = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
        fee = "0.00001"
        taker_gets = "3000000"
        taker_pays = "3000000"
        sequence = 0
        transaction = OfferCreateTransaction(
            account=account,
            fee=fee,
            sequence=sequence,
            taker_gets=taker_gets,
            taker_pays=taker_pays,
        )
        expected_dict = {
            "account": account,
            "fee": fee,
            "taker_gets": taker_gets,
            "taker_pays": taker_pays,
            "sequence": sequence,
            "transaction_type": "OfferCreate",
        }
        self.assertEqual(transaction.to_json(), expected_dict)

    def test_from_dict_to_json(self):
        account = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
        fee = "0.00001"
        taker_gets = {
            "currency": "BTC",
            "value": 100,
            "issuer": "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ",
        }
        taker_pays = "3000000"
        sequence = 0
        transaction_dict = {
            "account": account,
            "fee": fee,
            "taker_gets": taker_gets,
            "taker_pays": taker_pays,
            "sequence": sequence,
        }
        print(transaction_dict)
        transaction = OfferCreateTransaction.from_dict(transaction_dict)
        print(repr(transaction))
        expected_dict = {**transaction_dict, "transaction_type": "OfferCreate"}
        self.assertEqual(transaction.to_json(), expected_dict)
