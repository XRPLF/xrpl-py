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
    Request,
    Sign,
    SubmitMultisigned,
    SubmitOnly,
)
from xrpl.models.transactions import (
    CheckCreate,
    Memo,
    Payment,
    Signer,
    SignerEntry,
    SignerListSet,
    TrustSet,
    TrustSetFlag,
)
from xrpl.models.transactions.transaction import Transaction

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


class TestFromDict(TestCase):
    maxDiff = 2000

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
            "tx_json": transaction.to_xrpl(),
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
            "tx_json": transaction.to_xrpl(),
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
            "fee": 10,  # this should be a str instead ("10")
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

    def test_from_dict_explicit_none(self):
        dictionary = {
            "account": "rH6ZiHU1PGamME2LvVTxrgvfjQpppWKGmr",
            "fee": "10",
            "sequence": None,
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
            flags=TrustSetFlag.TF_SET_NO_RIPPLE.value,
            limit_amount=IssuedCurrencyAmount(
                currency="USD", issuer="raoV5dkC66XvGWjSzUhCUuuGM3YFTitMxT", value="100"
            ),
        )
        actual = TrustSet.from_dict(dictionary)
        self.assertEqual(actual, expected)

    def test_from_dict_with_str_enum_value(self):
        dictionary = {
            "method": "account_channels",
            "account": "rH6ZiHU1PGamME2LvVTxrgvfjQpppWKGmr",
            "limit": 100,
        }
        expected = AccountChannels(
            account="rH6ZiHU1PGamME2LvVTxrgvfjQpppWKGmr",
            limit=100,
        )
        actual = AccountChannels.from_dict(dictionary)
        self.assertEqual(actual, expected)

    def test_from_dict_bad_list(self):
        dictionary = {
            "account": "rpqBNcDpWaqZC2Rksayf8UyG66Fyv2JTQy",
            "fee": "10",
            "sequence": 16175710,
            "flags": 0,
            "signer_quorum": 1,
            "signer_entries": {
                "signer_entry": {
                    "account": "rJjusz1VauNA9XaHxJoiwHe38bmQFz1sUV",
                    "signer_weight": 1,
                }
            },  # this should be a List of signer entries instead
        }
        with self.assertRaises(XRPLModelException):
            SignerListSet.from_dict(dictionary)

    def test_from_dict_multisign(self):
        txn_sig1 = (
            "F80E201FE295AA08678F8542D8FC18EA18D582A0BD19BE77B9A24479418ADBCF4CAD28E7BD"
            "96137F88DE7736827C7AC6204FBA8DDADB7394E6D704CD1F4CD609"
        )
        txn_sig2 = (
            "036E95B8100EBA2A4A447A3AF24500261BF480A0E8D62EE15D03A697C85E73237A5202BD9A"
            "F2D9C68B8E8A5FA8B8DA4F8DABABE95E8401C5E57EC783291EF80C"
        )
        pubkey1 = "ED621D6D4FF54E809397195C4E24EF05E8500A7CE45CDD211F523A892CDBCDCDB2"
        pubkey2 = "EDD3ABCFF008ECE9ED3073B41913619341519BFF01F07331B56E5D6D2EC4A94A57"
        request = {
            "method": "submit_multisigned",
            "tx_json": {
                "Account": "rnD6t3JF9RTG4VgNLoc4i44bsQLgJUSi6h",
                "TransactionType": "TrustSet",
                "Fee": "10",
                "Sequence": 17896798,
                "Flags": 131072,
                "Signers": [
                    {
                        "Signer": {
                            "Account": "rGoKUCwJ2C4oHUsqnd8PVxZhFiBMV2T42G",
                            "TxnSignature": txn_sig1,
                            "SigningPubKey": pubkey1,
                        }
                    },
                    {
                        "Signer": {
                            "Account": "rsi3GL27pstEYUJ28ZM3q155rmFCCTBCZ1",
                            "TxnSignature": txn_sig2,
                            "SigningPubKey": pubkey2,
                        }
                    },
                ],
                "SigningPubKey": "",
                "LimitAmount": {
                    "currency": "USD",
                    "issuer": "rH5gvkKxGHrFAMAACeu9CB3FMu7pQ9jfZm",
                    "value": "10",
                },
            },
            "fail_hard": False,
        }
        expected = SubmitMultisigned(
            tx_json=TrustSet(
                account="rnD6t3JF9RTG4VgNLoc4i44bsQLgJUSi6h",
                fee="10",
                sequence=17896798,
                flags=131072,
                signers=[
                    Signer(
                        account="rGoKUCwJ2C4oHUsqnd8PVxZhFiBMV2T42G",
                        txn_signature=txn_sig1,
                        signing_pub_key=pubkey1,
                    ),
                    Signer(
                        account="rsi3GL27pstEYUJ28ZM3q155rmFCCTBCZ1",
                        txn_signature=txn_sig2,
                        signing_pub_key=pubkey2,
                    ),
                ],
                limit_amount=IssuedCurrencyAmount(
                    currency="USD",
                    issuer="rH5gvkKxGHrFAMAACeu9CB3FMu7pQ9jfZm",
                    value="10",
                ),
            ),
        )
        actual = Request.from_dict(request)
        self.assertEqual(actual, expected)

    def test_from_dict_submit(self):
        blob = "SOISUSF9SD0839W8U98J98SF"
        id_val = "submit_786514"
        request = {
            "method": "submit",
            "tx_blob": blob,
            "fail_hard": False,
            "id": id_val,
        }
        expected = SubmitOnly(tx_blob=blob, id=id_val)
        actual = Request.from_dict(request)
        self.assertEqual(actual, expected)

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
                    translated_tx = tx.to_xrpl()
                    self.assertEqual(x_json, translated_tx)
                with self.subTest(json=r_json):
                    tx = Transaction.from_xrpl(r_json)
                    translated_tx = tx.to_xrpl()
                    self.assertEqual(r_json, translated_tx)

    def test_from_xrpl_signers(self):
        txn_sig1 = (
            "F80E201FE295AA08678F8542D8FC18EA18D582A0BD19BE77B9A24479418ADBCF4CAD28E7BD"
            "96137F88DE7736827C7AC6204FBA8DDADB7394E6D704CD1F4CD609"
        )
        txn_sig2 = (
            "036E95B8100EBA2A4A447A3AF24500261BF480A0E8D62EE15D03A697C85E73237A5202BD9A"
            "F2D9C68B8E8A5FA8B8DA4F8DABABE95E8401C5E57EC783291EF80C"
        )
        pubkey1 = "ED621D6D4FF54E809397195C4E24EF05E8500A7CE45CDD211F523A892CDBCDCDB2"
        pubkey2 = "EDD3ABCFF008ECE9ED3073B41913619341519BFF01F07331B56E5D6D2EC4A94A57"
        tx = {
            "Account": "rnoGkgSpt6AX1nQxZ2qVGx7Fgw6JEcoQas",
            "TransactionType": "TrustSet",
            "Fee": "10",
            "Sequence": 17892983,
            "Flags": 131072,
            "Signers": [
                {
                    "Signer": {
                        "Account": "rGVXgBz4NraZcwi5vqpmwPW6P4y74A4YvX",
                        "TxnSignature": txn_sig1,
                        "SigningPubKey": pubkey1,
                    }
                },
                {
                    "Signer": {
                        "Account": "rB5q2wsHeXdQeh2KFzBb1CujNAfSKys6GN",
                        "TxnSignature": txn_sig2,
                        "SigningPubKey": pubkey2,
                    }
                },
            ],
            "SigningPubKey": "",
            "LimitAmount": {
                "currency": "USD",
                "issuer": "rBPvTKisx7UCGLDtiUZ6mDssXNREuVuL8Y",
                "value": "10",
            },
        }
        expected = TrustSet(
            account="rnoGkgSpt6AX1nQxZ2qVGx7Fgw6JEcoQas",
            fee="10",
            sequence=17892983,
            flags=131072,
            signers=[
                Signer(
                    account="rGVXgBz4NraZcwi5vqpmwPW6P4y74A4YvX",
                    txn_signature=txn_sig1,
                    signing_pub_key=pubkey1,
                ),
                Signer(
                    account="rB5q2wsHeXdQeh2KFzBb1CujNAfSKys6GN",
                    txn_signature=txn_sig2,
                    signing_pub_key=pubkey2,
                ),
            ],
            limit_amount=IssuedCurrencyAmount(
                currency="USD", issuer="rBPvTKisx7UCGLDtiUZ6mDssXNREuVuL8Y", value="10"
            ),
        )
        self.assertEqual(Transaction.from_xrpl(tx), expected)

    def test_from_xrpl_memos(self):
        memo_type = "687474703a2f2f6578616d706c652e636f6d2f6d656d6f2f67656e65726963"
        tx = {
            "Account": "rnoGkgSpt6AX1nQxZ2qVGx7Fgw6JEcoQas",
            "TransactionType": "TrustSet",
            "Fee": "10",
            "Sequence": 17892983,
            "Flags": 131072,
            "Memos": [
                {
                    "Memo": {
                        "MemoType": memo_type,
                        "MemoData": "72656e74",
                    }
                }
            ],
            "SigningPubKey": "",
            "LimitAmount": {
                "currency": "USD",
                "issuer": "rBPvTKisx7UCGLDtiUZ6mDssXNREuVuL8Y",
                "value": "10",
            },
        }
        expected = TrustSet(
            account="rnoGkgSpt6AX1nQxZ2qVGx7Fgw6JEcoQas",
            fee="10",
            sequence=17892983,
            flags=131072,
            memos=[
                Memo(
                    memo_type=memo_type,
                    memo_data="72656e74",
                )
            ],
            limit_amount=IssuedCurrencyAmount(
                currency="USD", issuer="rBPvTKisx7UCGLDtiUZ6mDssXNREuVuL8Y", value="10"
            ),
        )
        self.assertEqual(Transaction.from_xrpl(tx), expected)

    def test_to_xrpl_paths(self):
        paths_json = [
            [
                {"account": "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B", "type": 1},
                {
                    "currency": "USD",
                    "issuer": "rMwjYedjc7qqtKYVLiAccJSmCwih4LnE2q",
                    "type": 48,
                },
                {"account": "rMwjYedjc7qqtKYVLiAccJSmCwih4LnE2q", "type": 1},
                {"account": "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn", "type": 1},
            ],
        ]

        p = Payment(
            account="rweYz56rfmQ98cAdRaeTxQS9wVMGnrdsFp",
            amount=IssuedCurrencyAmount(
                currency="USD",
                issuer="rweYz56rfmQ98cAdRaeTxQS9wVMGnrdsFp",
                value="0.0001",
            ),
            destination="rweYz56rfmQ98cAdRaeTxQS9wVMGnrdsFp",
            send_max=IssuedCurrencyAmount(
                currency="BTC",
                issuer="rweYz56rfmQ98cAdRaeTxQS9wVMGnrdsFp",
                value="0.0000002831214446",
            ),
            paths=paths_json,
            sequence=290,
        )
        tx_json = p.to_xrpl()

        expected = {
            "Account": "rweYz56rfmQ98cAdRaeTxQS9wVMGnrdsFp",
            "TransactionType": "Payment",
            "Sequence": 290,
            "Flags": 0,
            "SigningPubKey": "",
            "Amount": {
                "currency": "USD",
                "issuer": "rweYz56rfmQ98cAdRaeTxQS9wVMGnrdsFp",
                "value": "0.0001",
            },
            "Destination": "rweYz56rfmQ98cAdRaeTxQS9wVMGnrdsFp",
            "Paths": [
                [
                    {"account": "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B", "type": 1},
                    {
                        "currency": "USD",
                        "issuer": "rMwjYedjc7qqtKYVLiAccJSmCwih4LnE2q",
                        "type": 48,
                    },
                    {"account": "rMwjYedjc7qqtKYVLiAccJSmCwih4LnE2q", "type": 1},
                    {"account": "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn", "type": 1},
                ]
            ],
            "SendMax": {
                "currency": "BTC",
                "issuer": "rweYz56rfmQ98cAdRaeTxQS9wVMGnrdsFp",
                "value": "0.0000002831214446",
            },
        }
        self.assertEqual(tx_json, expected)

    def test_to_xrpl_signer(self):
        tx = SignerListSet(
            account="rweYz56rfmQ98cAdRaeTxQS9wVMGnrdsFp",
            sequence=290,
            signer_quorum=1,
            signer_entries=[
                SignerEntry(
                    account="rMwjYedjc7qqtKYVLiAccJSmCwih4LnE2q",
                    signer_weight=1,
                ),
            ],
        )
        expected = {
            "Account": "rweYz56rfmQ98cAdRaeTxQS9wVMGnrdsFp",
            "TransactionType": "SignerListSet",
            "Sequence": 290,
            "Flags": 0,
            "SigningPubKey": "",
            "SignerQuorum": 1,
            "SignerEntries": [
                {
                    "SignerEntry": {
                        "Account": "rMwjYedjc7qqtKYVLiAccJSmCwih4LnE2q",
                        "SignerWeight": 1,
                    }
                }
            ],
        }
        self.assertEqual(tx.to_xrpl(), expected)
