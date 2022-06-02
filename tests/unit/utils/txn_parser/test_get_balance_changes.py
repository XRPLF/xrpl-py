from __future__ import annotations

import json
from unittest import TestCase

from xrpl.utils import get_balance_changes

path_to_json = "tests/unit/utils/txn_parser/transaction_jsons/"
with open(path_to_json + "payment_iou_destination_no_balance.json", "r") as infile:
    payment_iou_destination_no_balance = json.load(infile)
with open(path_to_json + "payment_iou_multipath.json", "r") as infile:
    payment_iou_multipath = json.load(infile)
with open(path_to_json + "payment_iou_redeem_then_issue.json", "r") as infile:
    payment_iou_redeem_then_issue = json.load(infile)
with open(path_to_json + "payment_iou_redeem.json", "r") as infile:
    payment_iou_redeem = json.load(infile)
with open(path_to_json + "payment_iou_spend_full_balance.json", "r") as infile:
    payment_iou_spend_full_balance = json.load(infile)
with open(path_to_json + "payment_iou.json", "r") as infile:
    payment_iou = json.load(infile)
with open(path_to_json + "payment_xrp_create_account.json", "r") as infile:
    payment_xrp_create_account = json.load(infile)
with open(path_to_json + "trustline_create.json", "r") as infile:
    trustline_create = json.load(infile)
with open(path_to_json + "trustline_delete.json", "r") as infile:
    trustline_delete = json.load(infile)
with open(path_to_json + "trustline_set_limit_zero.json", "r") as infile:
    trustline_set_limit_zero = json.load(infile)
with open(path_to_json + "trustline_set_limit.json", "r") as infile:
    trustline_set_limit = json.load(infile)
with open(path_to_json + "trustline_set_limit2.json", "r") as infile:
    trustline_set_limit2 = json.load(infile)


class TestGetBalanceChanges(TestCase):
    def test_payment_iou_destination_no_balance(self: TestGetBalanceChanges):
        actual = get_balance_changes(payment_iou_destination_no_balance["meta"])
        expected = [
            {
                "account": "rKmBGxocj9Abgy25J51Mk1iqFzW9aVF9Tc",
                "balances": [
                    {
                        "currency": "USD",
                        "issuer": "rMwjYedjc7qqtKYVLiAccJSmCwih4LnE2q",
                        "value": "-0.01",
                    },
                    {
                        "currency": "XRP",
                        "value": "-0.012",
                    },
                ],
            },
            {
                "account": "rMwjYedjc7qqtKYVLiAccJSmCwih4LnE2q",
                "balances": [
                    {
                        "currency": "USD",
                        "issuer": "rKmBGxocj9Abgy25J51Mk1iqFzW9aVF9Tc",
                        "value": "0.01",
                    },
                    {
                        "currency": "USD",
                        "issuer": "rLDYrujdKUfVx28T9vRDAbyJ7G2WVXKo4K",
                        "value": "-0.01",
                    },
                ],
            },
            {
                "account": "rLDYrujdKUfVx28T9vRDAbyJ7G2WVXKo4K",
                "balances": [
                    {
                        "currency": "USD",
                        "issuer": "rMwjYedjc7qqtKYVLiAccJSmCwih4LnE2q",
                        "value": "0.01",
                    },
                ],
            },
        ]
        self.assertEqual(actual, expected)

    def test_payment_iou_multipath(self: TestGetBalanceChanges):
        actual = get_balance_changes(payment_iou_multipath["meta"])
        expected = [
            {
                "account": "rrnsYgWn13Z28GtRgznrSUsLfMkvsXCZSu",
                "balances": [
                    {
                        "currency": "USD",
                        "issuer": "r4nmQNH4Fhjfh6cHDbvVSsBv7KySbj4cBf",
                        "value": "100",
                    },
                    {
                        "currency": "USD",
                        "issuer": "rnYDWQaRdMb5neCGgvFfhw3MBoxmv5LtfH",
                        "value": "-100",
                    },
                ],
            },
            {
                "account": "r4nmQNH4Fhjfh6cHDbvVSsBv7KySbj4cBf",
                "balances": [
                    {
                        "currency": "USD",
                        "issuer": "rrnsYgWn13Z28GtRgznrSUsLfMkvsXCZSu",
                        "value": "-100",
                    },
                    {
                        "currency": "XRP",
                        "value": "-0.00001",
                    },
                    {
                        "currency": "USD",
                        "issuer": "rJsaPnGdeo7BhMnHjuc3n44Mf7Ra1qkSVJ",
                        "value": "-100",
                    },
                    {
                        "currency": "USD",
                        "issuer": "rGpeQzUWFu4fMhJHZ1Via5aqFC3A5twZUD",
                        "value": "-100",
                    },
                ],
            },
            {
                "account": "rJsaPnGdeo7BhMnHjuc3n44Mf7Ra1qkSVJ",
                "balances": [
                    {
                        "currency": "USD",
                        "issuer": "r4nmQNH4Fhjfh6cHDbvVSsBv7KySbj4cBf",
                        "value": "100",
                    },
                    {
                        "currency": "USD",
                        "issuer": "rnYDWQaRdMb5neCGgvFfhw3MBoxmv5LtfH",
                        "value": "-100",
                    },
                ],
            },
            {
                "account": "rGpeQzUWFu4fMhJHZ1Via5aqFC3A5twZUD",
                "balances": [
                    {
                        "currency": "USD",
                        "issuer": "r4nmQNH4Fhjfh6cHDbvVSsBv7KySbj4cBf",
                        "value": "100",
                    },
                    {
                        "currency": "USD",
                        "issuer": "rnYDWQaRdMb5neCGgvFfhw3MBoxmv5LtfH",
                        "value": "-100",
                    },
                ],
            },
            {
                "account": "rnYDWQaRdMb5neCGgvFfhw3MBoxmv5LtfH",
                "balances": [
                    {
                        "currency": "USD",
                        "issuer": "rJsaPnGdeo7BhMnHjuc3n44Mf7Ra1qkSVJ",
                        "value": "100",
                    },
                    {
                        "currency": "USD",
                        "issuer": "rrnsYgWn13Z28GtRgznrSUsLfMkvsXCZSu",
                        "value": "100",
                    },
                    {
                        "currency": "USD",
                        "issuer": "rGpeQzUWFu4fMhJHZ1Via5aqFC3A5twZUD",
                        "value": "100",
                    },
                ],
            },
        ]
        self.assertEqual(actual, expected)

    def test_payment_iou_redeem_then_issue(self: TestGetBalanceChanges):
        actual = get_balance_changes(payment_iou_redeem_then_issue["meta"])
        expected = [
            {
                "account": "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                "balances": [
                    {
                        "currency": "USD",
                        "issuer": "rPMh7Pi9ct699iZUTWaytJUoHcJ7cgyziK",
                        "value": "200",
                    }
                ],
            },
            {
                "account": "rPMh7Pi9ct699iZUTWaytJUoHcJ7cgyziK",
                "balances": [
                    {
                        "currency": "USD",
                        "issuer": "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                        "value": "-200",
                    },
                    {"currency": "XRP", "value": "-0.00001"},
                ],
            },
        ]
        self.assertEqual(actual, expected)

    def test_payment_iou_redeem(self: TestGetBalanceChanges):
        actual = get_balance_changes(payment_iou_redeem["meta"])
        expected = [
            {
                "account": "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                "balances": [
                    {
                        "currency": "USD",
                        "issuer": "rPMh7Pi9ct699iZUTWaytJUoHcJ7cgyziK",
                        "value": "100",
                    },
                ],
            },
            {
                "account": "rPMh7Pi9ct699iZUTWaytJUoHcJ7cgyziK",
                "balances": [
                    {
                        "currency": "USD",
                        "issuer": "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                        "value": "-100",
                    },
                    {
                        "currency": "XRP",
                        "value": "-0.00001",
                    },
                ],
            },
        ]
        self.assertEqual(actual, expected)

    def test_payment_iou_spend_full_balance(self: TestGetBalanceChanges):
        actual = get_balance_changes(payment_iou_spend_full_balance["meta"])
        expected = [
            {
                "account": "rKmBGxocj9Abgy25J51Mk1iqFzW9aVF9Tc",
                "balances": [
                    {
                        "currency": "USD",
                        "issuer": "rMwjYedjc7qqtKYVLiAccJSmCwih4LnE2q",
                        "value": "0.2",
                    }
                ],
            },
            {
                "account": "rMwjYedjc7qqtKYVLiAccJSmCwih4LnE2q",
                "balances": [
                    {
                        "currency": "USD",
                        "issuer": "rKmBGxocj9Abgy25J51Mk1iqFzW9aVF9Tc",
                        "value": "-0.2",
                    },
                    {
                        "currency": "USD",
                        "issuer": "rLDYrujdKUfVx28T9vRDAbyJ7G2WVXKo4K",
                        "value": "0.2",
                    },
                ],
            },
            {
                "account": "rLDYrujdKUfVx28T9vRDAbyJ7G2WVXKo4K",
                "balances": [
                    {
                        "currency": "USD",
                        "issuer": "rMwjYedjc7qqtKYVLiAccJSmCwih4LnE2q",
                        "value": "-0.2",
                    },
                    {
                        "currency": "XRP",
                        "value": "-0.012",
                    },
                ],
            },
        ]
        self.assertEqual(actual, expected)

    def test_payment_iou(self: TestGetBalanceChanges):
        actual = get_balance_changes(payment_iou["meta"])
        expected = [
            {
                "account": "rKmBGxocj9Abgy25J51Mk1iqFzW9aVF9Tc",
                "balances": [
                    {
                        "currency": "USD",
                        "issuer": "rMwjYedjc7qqtKYVLiAccJSmCwih4LnE2q",
                        "value": "-0.01",
                    },
                    {
                        "currency": "XRP",
                        "value": "-0.012",
                    },
                ],
            },
            {
                "account": "rMwjYedjc7qqtKYVLiAccJSmCwih4LnE2q",
                "balances": [
                    {
                        "currency": "USD",
                        "issuer": "rKmBGxocj9Abgy25J51Mk1iqFzW9aVF9Tc",
                        "value": "0.01",
                    },
                    {
                        "currency": "USD",
                        "issuer": "rLDYrujdKUfVx28T9vRDAbyJ7G2WVXKo4K",
                        "value": "-0.01",
                    },
                ],
            },
            {
                "account": "rLDYrujdKUfVx28T9vRDAbyJ7G2WVXKo4K",
                "balances": [
                    {
                        "currency": "USD",
                        "issuer": "rMwjYedjc7qqtKYVLiAccJSmCwih4LnE2q",
                        "value": "0.01",
                    },
                ],
            },
        ]
        self.assertEqual(actual, expected)

    def test_payment_xrp_create_account(self: TestGetBalanceChanges):
        actual = get_balance_changes(payment_xrp_create_account["meta"])
        expected = [
            {
                "account": "rLDYrujdKUfVx28T9vRDAbyJ7G2WVXKo4K",
                "balances": [
                    {
                        "currency": "XRP",
                        "value": "100",
                    }
                ],
            },
            {
                "account": "rKmBGxocj9Abgy25J51Mk1iqFzW9aVF9Tc",
                "balances": [
                    {
                        "currency": "XRP",
                        "value": "-100.012",
                    }
                ],
            },
        ]
        self.assertEqual(actual, expected)

    def test_trustline_create(self: TestGetBalanceChanges):
        actual = get_balance_changes(trustline_create["meta"])
        expected = [
            {
                "account": "rLDYrujdKUfVx28T9vRDAbyJ7G2WVXKo4K",
                "balances": [
                    {
                        "currency": "USD",
                        "issuer": "rMwjYedjc7qqtKYVLiAccJSmCwih4LnE2q",
                        "value": "10",
                    },
                    {
                        "currency": "XRP",
                        "value": "-0.012",
                    },
                ],
            },
            {
                "account": "rMwjYedjc7qqtKYVLiAccJSmCwih4LnE2q",
                "balances": [
                    {
                        "currency": "USD",
                        "issuer": "rLDYrujdKUfVx28T9vRDAbyJ7G2WVXKo4K",
                        "value": "-10",
                    }
                ],
            },
        ]
        self.assertEqual(actual, expected)

    def test_trustline_delete(self: TestGetBalanceChanges):
        actual = get_balance_changes(trustline_delete["meta"])
        expected = [
            {
                "account": "rKmBGxocj9Abgy25J51Mk1iqFzW9aVF9Tc",
                "balances": [
                    {
                        "currency": "USD",
                        "issuer": "rMwjYedjc7qqtKYVLiAccJSmCwih4LnE2q",
                        "value": "0.02",
                    }
                ],
            },
            {
                "account": "rMwjYedjc7qqtKYVLiAccJSmCwih4LnE2q",
                "balances": [
                    {
                        "currency": "USD",
                        "issuer": "rKmBGxocj9Abgy25J51Mk1iqFzW9aVF9Tc",
                        "value": "-0.02",
                    },
                    {
                        "currency": "USD",
                        "issuer": "rLDYrujdKUfVx28T9vRDAbyJ7G2WVXKo4K",
                        "value": "0.02",
                    },
                ],
            },
            {
                "account": "rLDYrujdKUfVx28T9vRDAbyJ7G2WVXKo4K",
                "balances": [
                    {
                        "currency": "USD",
                        "issuer": "rMwjYedjc7qqtKYVLiAccJSmCwih4LnE2q",
                        "value": "-0.02",
                    },
                    {
                        "currency": "XRP",
                        "value": "-0.012",
                    },
                ],
            },
        ]
        self.assertEqual(actual, expected)

    def test_trustline_set_limit_zero(self: TestGetBalanceChanges):
        actual = get_balance_changes(trustline_set_limit_zero["meta"])
        expected = [
            {
                "account": "rLDYrujdKUfVx28T9vRDAbyJ7G2WVXKo4K",
                "balances": [
                    {
                        "currency": "XRP",
                        "value": "-0.012",
                    }
                ],
            },
        ]
        self.assertEqual(actual, expected)

    def test_trustline_set_limit(self: TestGetBalanceChanges):
        actual = get_balance_changes(trustline_set_limit["meta"])
        expected = [
            {
                "account": "rLDYrujdKUfVx28T9vRDAbyJ7G2WVXKo4K",
                "balances": [
                    {
                        "currency": "XRP",
                        "value": "-0.012",
                    }
                ],
            }
        ]
        self.assertEqual(actual, expected)

    def test_trustline_set_limit2(self: TestGetBalanceChanges):
        actual = get_balance_changes(trustline_set_limit2["meta"])
        expected = [
            {
                "account": "rsApBGKJmMfExxZBrGnzxEXyq7TMhMRg4e",
                "balances": [
                    {
                        "currency": "XRP",
                        "value": "-0.00001",
                    }
                ],
            }
        ]
        self.assertEqual(actual, expected)
