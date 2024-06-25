from unittest import TestCase

from xrpl.models.amounts.issued_currency_amount import IssuedCurrencyAmount
from xrpl.models.auth_account import AuthAccount
from xrpl.models.currencies.issued_currency import IssuedCurrency
from xrpl.models.currencies.xrp import XRP
from xrpl.models.ledger_objects.amm import AMM, AuctionSlot, VoteEntry
from xrpl.models.ledger_objects.ledger_object import LedgerObject


class TestAMM(TestCase):
    def test_amm(self):
        amm_json = {
            "Account": "rE54zDvgnghAoPopCgvtiqWNq3dU5y836S",
            "Asset": {"currency": "XRP"},
            "Asset2": {
                "currency": "TST",
                "issuer": "rP9jPyP5kyvFRb6ZiRghAGw5u8SGAmU4bd",
            },
            "AuctionSlot": {
                "Account": "rJVUeRqDFNs2xqA7ncVE6ZoAhPUoaJJSQm",
                "AuthAccounts": [
                    {"AuthAccount": {"Account": "rMKXGCbJ5d8LbrqthdG46q3f969MVK2Qeg"}},
                    {"AuthAccount": {"Account": "rBepJuTLFJt3WmtLXYAxSjtBWAeQxVbncv"}},
                ],
                "DiscountedFee": 0,
                "Expiration": 721870180,
                "Price": {
                    "currency": "039C99CD9AB0B70B32ECDA51EAAE471625608EA2",
                    "issuer": "rE54zDvgnghAoPopCgvtiqWNq3dU5y836S",
                    "value": "0.8696263565463045",
                },
            },
            "LPTokenBalance": {
                "currency": "039C99CD9AB0B70B32ECDA51EAAE471625608EA2",
                "issuer": "rE54zDvgnghAoPopCgvtiqWNq3dU5y836S",
                "value": "71150.53584131501",
            },
            "TradingFee": 600,
            "VoteSlots": [
                {
                    "VoteEntry": {
                        "Account": "rJVUeRqDFNs2xqA7ncVE6ZoAhPUoaJJSQm",
                        "TradingFee": 600,
                        "VoteWeight": 100000,
                    }
                }
            ],
            "OwnerNode": "0",
            "Flags": 0,
            "LedgerEntryType": "AMM",
        }
        actual = LedgerObject.from_xrpl(amm_json)
        expected = AMM(
            account="rE54zDvgnghAoPopCgvtiqWNq3dU5y836S",
            asset=XRP(),
            asset2=IssuedCurrency(
                currency="TST",
                issuer="rP9jPyP5kyvFRb6ZiRghAGw5u8SGAmU4bd",
            ),
            auction_slot=AuctionSlot(
                account="rJVUeRqDFNs2xqA7ncVE6ZoAhPUoaJJSQm",
                auth_accounts=[
                    AuthAccount(account="rMKXGCbJ5d8LbrqthdG46q3f969MVK2Qeg"),
                    AuthAccount(account="rBepJuTLFJt3WmtLXYAxSjtBWAeQxVbncv"),
                ],
                discounted_fee=0,
                expiration=721870180,
                price=IssuedCurrencyAmount(
                    currency="039C99CD9AB0B70B32ECDA51EAAE471625608EA2",
                    issuer="rE54zDvgnghAoPopCgvtiqWNq3dU5y836S",
                    value="0.8696263565463045",
                ),
            ),
            owner_node="0",
            lp_token_balance=IssuedCurrencyAmount(
                currency="039C99CD9AB0B70B32ECDA51EAAE471625608EA2",
                issuer="rE54zDvgnghAoPopCgvtiqWNq3dU5y836S",
                value="71150.53584131501",
            ),
            trading_fee=600,
            vote_slots=[
                VoteEntry(
                    account="rJVUeRqDFNs2xqA7ncVE6ZoAhPUoaJJSQm",
                    trading_fee=600,
                    vote_weight=100000,
                ),
            ],
        )
        self.assertEqual(actual, expected)
