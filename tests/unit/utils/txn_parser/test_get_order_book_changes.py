from __future__ import annotations

import json
from unittest import TestCase

from xrpl.utils import get_order_book_changes

path_to_json = "tests/unit/utils/txn_parser/transaction_jsons/"
with open(path_to_json + "offer_created.json", "r") as infile:
    offer_created = json.load(infile)
with open(path_to_json + "offer_partially_filled_and_filled.json", "r") as infile:
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
                "maker_account": "rJHbqhp9Sea4f43RoUanrDE1gW9MymTLp9",
                "offer_changes": [
                    {
                        "flags": 131072,
                        "taker_gets": {"currency": "XRP", "value": "44.930000"},
                        "taker_pays": {
                            "currency": "USD",
                            "issuer": "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
                            "value": "14.524821",
                        },
                        "sequence": 71307620,
                        "status": "created",
                        "maker_exchange_rate": "0.3232766748275094591586912976",
                        "expiration_time": 740218424,
                    }
                ],
            }
        ]
        self.assertEqual(actual, expected)

    def test_offer_partially_filled_and_filled(self: TestGetOrderBookChanges):
        actual = get_order_book_changes(offer_partially_filled_and_filled["meta"])
        expected = [
            {
                "maker_account": "rNzgS71DyJPMnWMA8aS7NqvXP7bNuwyaZo",
                "offer_changes": [
                    {
                        "flags": 131072,
                        "taker_gets": {
                            "currency": "USD",
                            "issuer": "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq",
                            "value": "-63.7479881398749",
                        },
                        "taker_pays": {
                            "currency": "USD",
                            "issuer": "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
                            "value": "-62.4730283770749",
                        },
                        "sequence": 5931,
                        "status": "filled",
                        "maker_exchange_rate": "0.9799999999999607517025555356",
                    }
                ],
            },
            {
                "maker_account": "rPu2feBaViWGmWJhvaF5yLocTVD8FUxd2A",
                "offer_changes": [
                    {
                        "flags": 131072,
                        "taker_gets": {
                            "currency": "USD",
                            "issuer": "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq",
                            "value": "-117.3895136925395",
                        },
                        "taker_pays": {
                            "currency": "USD",
                            "issuer": "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
                            "value": "-115.0877585220975",
                        },
                        "sequence": 67701941,
                        "status": "partially-filled",
                        "maker_exchange_rate": "0.980392156862744680458408839",
                    }
                ],
            },
        ]
        self.assertEqual(actual, expected)

    def test_offer_cancelled(self: TestGetOrderBookChanges):
        actual = get_order_book_changes(offer_cancelled["meta"])
        expected = [
            {
                "maker_account": "rEUt5Wy44vDKBDaGkUWG6oSTvxmqgnKWCg",
                "offer_changes": [
                    {
                        "flags": 0,
                        "taker_gets": {
                            "currency": "XDX",
                            "issuer": "rMJAXYsbNzhwp7FfYnAsYP5ty3R9XnurPo",
                            "value": "-82335.52909",
                        },
                        "taker_pays": {"currency": "XRP", "value": "-47.504858"},
                        "sequence": 70922543,
                        "status": "cancelled",
                        "maker_exchange_rate": "0.0005769666937838341642215588998",
                    }
                ],
            }
        ]
        self.assertEqual(actual, expected)

    def test_offer_with_expiration(self: TestGetOrderBookChanges):
        actual = get_order_book_changes(offer_with_expiration["meta"])
        expected = [
            {
                "maker_account": "rJHHRtt6qmiz71tyGFMZUoxMGakdgqEou5",
                "offer_changes": [
                    {
                        "flags": 0,
                        "taker_gets": {"currency": "XRP", "value": "-50.000000"},
                        "taker_pays": {
                            "currency": "457175696C69627269756D000000000000000000",
                            "issuer": "rpakCr61Q92abPXJnVboKENmpKssWyHpwu",
                            "value": "-230.8404670389911",
                        },
                        "sequence": 67782876,
                        "status": "cancelled",
                        "maker_exchange_rate": "4.616809340779822",
                        "expiration_time": 708682031,
                    }
                ],
            }
        ]
        self.assertEqual(actual, expected)
