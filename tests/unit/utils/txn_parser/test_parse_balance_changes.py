from __future__ import annotations

from unittest import TestCase

from tests.unit.utils.txn_parser.transaction import TXN
from xrpl.utils import parse_balance_changes


class TestParseBalanceChanges(TestCase):
    def test(self: TestParseBalanceChanges):
        actual = parse_balance_changes(transaction=TXN)
        excpected = {
            "rwwyrB83G6hS8vp4oLMqwRiMNLWToVCX6L": [
                {
                    "issuer": "rLBnhMjV6ifEHYeV4gaS6jPKerZhQddFxW",
                    "currency": "5452535259000000000000000000000000000000",
                    "value": "10",
                }
            ],
            "rLBnhMjV6ifEHYeV4gaS6jPKerZhQddFxW": [
                {
                    "issuer": "rwwyrB83G6hS8vp4oLMqwRiMNLWToVCX6L",
                    "currency": "5452535259000000000000000000000000000000",
                    "value": "-10",
                },
                {
                    "issuer": "rME2LXH8Che2BZRbu5LCRKWju9U3ARaEPd",
                    "currency": "5452535259000000000000000000000000000000",
                    "value": "10",
                },
            ],
            "rME2LXH8Che2BZRbu5LCRKWju9U3ARaEPd": [
                {
                    "issuer": "rLBnhMjV6ifEHYeV4gaS6jPKerZhQddFxW",
                    "currency": "5452535259000000000000000000000000000000",
                    "value": "-10",
                },
                {"issuer": "", "currency": "XRP", "value": "-0.000012"},
            ],
        }
        self.assertEqual(first=actual, second=excpected)
