import json
import os
from unittest import TestCase

from xrpl.models import XRPLModelException
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.requests import (
    AccountChannels,
    BookOffers,
    PathFind,
    PathFindSubcommand,
    PathStep,
    Sign,
)
from xrpl.models.transactions import (
    CheckCreate,
    SignerEntry,
    SignerListSet,
    TrustSet,
    TrustSetFlag,
)
from xrpl.models.transactions.transaction import Transaction
from xrpl.transaction import transaction_json_to_binary_codec_form

currency = "BTC"
value = "100"
issuer = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
amount_dict = {
    "currency": currency,
    "issuer": issuer,
    "value": value,
}

account = issuer
destination = issuer
send_max = amount_dict
check_create_dict = {
    "account": account,
    "destination": destination,
    "send_max": send_max,
}

secret = "topsecretpassword"


class TestBaseModel(TestCase):
    maxDiff = 1000

    def test_eq(self):
        amount = IssuedCurrencyAmount(**amount_dict)
        self.assertEqual(amount, IssuedCurrencyAmount(**amount_dict))

    def test_repr(self):
        amount = IssuedCurrencyAmount(**amount_dict)
        expected_repr = (
            f"IssuedCurrencyAmount(currency='{currency}', "
            f"issuer='{issuer}', value='{value}')"
        )
        self.assertEqual(repr(amount), expected_repr)

    def test_from_dict_basic(self):
        amount = IssuedCurrencyAmount.from_dict(amount_dict)
        self.assertEqual(amount, IssuedCurrencyAmount(**amount_dict))

    def test_from_dict_recursive_amount(self):
        check_create = CheckCreate.from_dict(check_create_dict)

        expected_dict = {
            **check_create_dict,
            "transaction_type": "CheckCreate",
            "flags": 0,
            "signing_pub_key": "",
        }
        self.assertEqual(expected_dict, check_create.to_dict())

    def test_from_dict_recursive_currency(self):
        xrp = {"currency": "XRP"}
        issued_currency = {
            "currency": currency,
            "issuer": issuer,
        }
        book_offers_dict = {
            "taker_gets": xrp,
            "taker_pays": issued_currency,
        }
        book_offers = BookOffers.from_dict(book_offers_dict)

        expected_dict = {
            **book_offers_dict,
            "method": "book_offers",
            "taker_gets": {"currency": "XRP"},
        }
        self.assertEqual(expected_dict, book_offers.to_dict())

    def test_from_dict_recursive_transaction(self):
        transaction = CheckCreate.from_dict(check_create_dict)
        sign_dict = {"secret": secret, "transaction": transaction.to_dict()}
        sign = Sign.from_dict(sign_dict)

        expected_dict = {
            **sign_dict,
            "tx_json": transaction.to_dict(),
            "method": "sign",
            "fee_mult_max": 10,
            "fee_div_max": 1,
            "offline": False,
        }
        del expected_dict["transaction"]
        self.assertEqual(expected_dict, sign.to_dict())

    def test_from_dict_recursive_transaction_tx_json(self):
        transaction = CheckCreate.from_dict(check_create_dict)
        sign_dict = {"secret": secret, "tx_json": transaction.to_dict()}
        sign = Sign.from_dict(sign_dict)

        expected_dict = {
            **sign_dict,
            "tx_json": transaction.to_dict(),
            "method": "sign",
            "fee_mult_max": 10,
            "fee_div_max": 1,
            "offline": False,
        }
        self.assertEqual(expected_dict, sign.to_dict())

    def test_from_dict_signer(self):
        dictionary = {
            "account": "rpqBNcDpWaqZC2Rksayf8UyG66Fyv2JTQy",
            "fee": "10",
            "sequence": 16175710,
            "flags": 0,
            "signer_quorum": 1,
            "signer_entries": [
                {
                    "signer_entry": {
                        "account": "rJjusz1VauNA9XaHxJoiwHe38bmQFz1sUV",
                        "signer_weight": 1,
                    }
                }
            ],
        }
        expected = SignerListSet(
            account="rpqBNcDpWaqZC2Rksayf8UyG66Fyv2JTQy",
            fee="10",
            sequence=16175710,
            flags=0,
            signer_quorum=1,
            signer_entries=[
                SignerEntry(
                    account="rJjusz1VauNA9XaHxJoiwHe38bmQFz1sUV", signer_weight=1
                )
            ],
        )
        actual = SignerListSet.from_dict(dictionary)
        self.assertEqual(actual, expected)

    def test_from_dict_trust_set(self):
        dictionary = {
            "account": "rH6ZiHU1PGamME2LvVTxrgvfjQpppWKGmr",
            "fee": "10",
            "sequence": 16178313,
            "flags": TrustSetFlag.TF_SET_NO_RIPPLE,
            "limit_amount": {
                "currency": "USD",
                "issuer": "raoV5dkC66XvGWjSzUhCUuuGM3YFTitMxT",
                "value": "100",
            },
        }
        expected = TrustSet(
            account="rH6ZiHU1PGamME2LvVTxrgvfjQpppWKGmr",
            fee="10",
            sequence=16178313,
            flags=TrustSetFlag.TF_SET_NO_RIPPLE.value,
            limit_amount=IssuedCurrencyAmount(
                currency="USD", issuer="raoV5dkC66XvGWjSzUhCUuuGM3YFTitMxT", value="100"
            ),
        )
        actual = TrustSet.from_dict(dictionary)
        self.assertEqual(actual, expected)

    def test_from_dict_list_of_lists(self):
        path_step_dict = {"account": "rH6ZiHU1PGamME2LvVTxrgvfjQpppWKGmr"}
        path_find_dict = {
            "subcommand": PathFindSubcommand.CREATE,
            "source_account": "raoV5dkC66XvGWjSzUhCUuuGM3YFTitMxT",
            "destination_account": "rJjusz1VauNA9XaHxJoiwHe38bmQFz1sUV",
            "destination_amount": "100",
            "paths": [[path_step_dict]],
        }
        path_step = PathStep.from_dict(path_step_dict)
        expected = PathFind(
            subcommand=PathFindSubcommand.CREATE,
            source_account="raoV5dkC66XvGWjSzUhCUuuGM3YFTitMxT",
            destination_account="rJjusz1VauNA9XaHxJoiwHe38bmQFz1sUV",
            destination_amount="100",
            paths=[[path_step]],
        )
        actual = PathFind.from_dict(path_find_dict)
        self.assertEqual(actual, expected)

    def test_from_dict_any(self):
        account_channels_dict = {
            "account": "rH6ZiHU1PGamME2LvVTxrgvfjQpppWKGmr",
            "marker": "something",
        }
        expected = AccountChannels(**account_channels_dict)
        actual = AccountChannels.from_dict(account_channels_dict)
        self.assertEqual(actual, expected)

    def test_from_dict_bad_str(self):
        dictionary = {
            "account": "rH6ZiHU1PGamME2LvVTxrgvfjQpppWKGmr",
            "fee": 10,
            "sequence": 16178313,
            "flags": 131072,
            "limit_amount": {
                "currency": "USD",
                "issuer": "raoV5dkC66XvGWjSzUhCUuuGM3YFTitMxT",
                "value": "100",
            },
        }
        with self.assertRaises(XRPLModelException):
            TrustSet.from_dict(dictionary)

    def test_from_xrpl(self):
        dirname = os.path.dirname(__file__)
        full_filename = "x-codec-fixtures.json"
        absolute_path = os.path.join(dirname, full_filename)
        with open(absolute_path) as fixtures_file:
            fixtures_json = json.load(fixtures_file)
            for test in fixtures_json["transactions"]:
                x_json = test["xjson"]
                r_json = test["rjson"]
                with self.subTest(json=x_json):
                    tx = Transaction.from_xrpl(x_json)
                    translated_tx = transaction_json_to_binary_codec_form(tx.to_dict())
                    self.assertEqual(x_json, translated_tx)
                with self.subTest(json=r_json):
                    tx = Transaction.from_xrpl(r_json)
                    translated_tx = transaction_json_to_binary_codec_form(tx.to_dict())
                    self.assertEqual(r_json, translated_tx)

    def test_is_dict_of_model_when_true(self):
        self.assertTrue(
            IssuedCurrencyAmount.is_dict_of_model(
                IssuedCurrencyAmount.from_dict(amount_dict).to_dict(),
            ),
        )

    def test_is_dict_of_model_when_not_true(self):
        self.assertFalse(
            Sign.is_dict_of_model(
                IssuedCurrencyAmount.from_dict(amount_dict).to_dict(),
            ),
        )
