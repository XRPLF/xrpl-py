from __future__ import annotations
import json
from unittest import TestCase

from xrpl.utils import get_order_book_changes

path_to_json = "tests/unit/utils/txn_parser/transaction_jsons/"
with open(path_to_json + "offer_created.json", "r") as infile:
    offer_created = json.load(infile)
with open(path_to_json + "offer_partially-filled_and_filled.json", "r") as infile:
    offer_partially_filled_and_filled = json.load(infile)
with open(path_to_json + "offer_cancelled.json", "r") as infile:
    offer_cancelled = json.load(infile)
with open(path_to_json + "offer_with_expiration.json", "r") as infile:
    offer_with_expiration = json.load(infile)


class TestGetOrderBookChanges(TestCase):
    def test_offer_created(self: TestGetOrderBookChanges):
        actual = get_order_book_changes(offer_created["meta"])
        expected = [
            {
                "account": "rJHbqhp9Sea4f43RoUanrDE1gW9MymTLp9",
                "offer_changes": [
                    {
                        "direction": "sell",
                        "quantity": {
                            "currency": "XRP",
                            "value": "44.930000",
                        },
                        "total_price": {
                            "currency": "USD",
                            "issuer": "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
                            "value": "14.524821",
                        },
                        "sequence": 71307620,
                        "status": "created",
                        "maker_exchange_rate": "0.3232766748275095",
                        "expiration_time": 1686903224,
                    }
                ],
            },
        ]
        self.assertEqual(actual, expected)

    def test_offer_partially_filled_and_filled(self: TestGetOrderBookChanges):
        actual = get_order_book_changes(offer_partially_filled_and_filled["meta"])
        expected = [
            {
                "account": "rNzgS71DyJPMnWMA8aS7NqvXP7bNuwyaZo",
                "offer_changes": [
                    {
                        "direction": "sell",
                        "quantity": {
                            "currency": "USD",
                            "issuer": "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq",
                            "value": "63.7479881398749",
                        },
                        "total_price": {
                            "currency": "USD",
                            "issuer": "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
                            "value": "62.4730283770749",
                        },
                        "sequence": 5931,
                        "status": "filled",
                        "maker_exchange_rate": "0.98",
                    }
                ],
            },
            {
                "account": "rPu2feBaViWGmWJhvaF5yLocTVD8FUxd2A",
                "offer_changes": [
                    {
                        "direction": "sell",
                        "quantity": {
                            "currency": "USD",
                            "issuer": "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq",
                            "value": "117.3895136925395",
                        },
                        "total_price": {
                            "currency": "USD",
                            "issuer": "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
                            "value": "115.0877585220975",
                        },
                        "sequence": 67701941,
                        "status": "partially-filled",
                        "maker_exchange_rate": "0.9803921568627452",
                    }
                ],
            },
        ]
        self.assertEqual(actual, expected)

    def test_offer_cancelled(self: TestGetOrderBookChanges):
        actual = get_order_book_changes(offer_cancelled["meta"])
        expected = [
            {
                "account": "rEUt5Wy44vDKBDaGkUWG6oSTvxmqgnKWCg",
                "offer_changes": [
                    {
                        "direction": "buy",
                        "quantity": {
                            "currency": "XRP",
                            "value": "47.504858",
                        },
                        "total_price": {
                            "currency": "XDX",
                            "issuer": "rMJAXYsbNzhwp7FfYnAsYP5ty3R9XnurPo",
                            "value": "82335.52909",
                        },
                        "sequence": 70922543,
                        "status": "cancelled",
                        "maker_exchange_rate": "576966693.7838342",
                    }
                ],
            },
        ]
        self.assertEqual(actual, expected)

    def test_offer_with_expiration(self: TestGetOrderBookChanges):
        actual = get_order_book_changes(offer_with_expiration["meta"])
        expected = [
            {
                "account": "rJHHRtt6qmiz71tyGFMZUoxMGakdgqEou5",
                "offer_changes": [
                    {
                        "direction": "buy",
                        "quantity": {
                            "currency": "457175696C69627269756D000000000000000000",
                            "issuer": "rpakCr61Q92abPXJnVboKENmpKssWyHpwu",
                            "value": "230.7776699646076",
                        },
                        "total_price": {
                            "currency": "XRP",
                            "value": "50.000000",
                        },
                        "sequence": 67782878,
                        "status": "created",
                        "maker_exchange_rate": "4.615553399292152",
                        "expiration_time": 1655366861,
                    },
                    {
                        "direction": "buy",
                        "quantity": {
                            "currency": "457175696C69627269756D000000000000000000",
                            "issuer": "rpakCr61Q92abPXJnVboKENmpKssWyHpwu",
                            "value": "230.8404670389911",
                        },
                        "total_price": {
                            "currency": "XRP",
                            "value": "50.000000",
                        },
                        "sequence": 67782876,
                        "status": "cancelled",
                        "maker_exchange_rate": "4.616809340779822",
                        "expiration_time": 1655366831,
                    },
                ],
            },
        ]
        self.assertEqual(actual, expected)


# get_order_book_changes(offer_created["meta"])
