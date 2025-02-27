import json
import os
from unittest import TestCase

from xrpl.models import XRPLModelException
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.currencies import XRP, IssuedCurrency
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
from xrpl.models.requests.request import _DEFAULT_API_VERSION
from xrpl.models.transactions import (
    AMMBid,
    AuthAccount,
    CheckCreate,
    Memo,
    Payment,
    Signer,
    SignerEntry,
    SignerListSet,
    TrustSet,
    TrustSetFlag,
    XChainAddAccountCreateAttestation,
    XChainClaim,
)
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.xchain_bridge import XChainBridge

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

    def test_bad_type(self):
        transaction_dict = {
            "account": 1,
            "amount": 10,
            "destination": 2,
        }
        with self.assertRaises(XRPLModelException) as e:
            Payment(**transaction_dict)
        self.assertEqual(
            e.exception.args[0],
            str(
                {
                    "account": "account is <class 'int'>, expected <class 'str'>",
                    "amount": (
                        "amount is <class 'int'>, expected typing.Union[xrpl."
                        "models.amounts.issued_currency_amount.IssuedCurrencyAmount, "
                        "xrpl.models.amounts.mpt_amount.MPTAmount, str]"
                    ),
                    "destination": (
                        "destination is <class 'int'>, expected " "<class 'str'>"
                    ),
                }
            ),
        )

    def test_bad_type_flags(self):
        transaction_dict = {
            "account": account,
            "amount": value,
            "destination": destination,
            "flags": "1234",  # should be an int
        }
        with self.assertRaises(XRPLModelException) as e:
            Payment(**transaction_dict)
        self.assertEqual(
            e.exception.args[0],
            str(
                {
                    "flags": (
                        "flags is <class 'str'>, expected "
                        "typing.Union[typing.Dict[str, bool], int, typing.List[int]]"
                    ),
                    "destination": (
                        "An XRP payment transaction cannot have the same "
                        "sender and destination."
                    ),
                }
            ),
        )

    def test_bad_type_enum(self):
        path_find_dict = {
            "subcommand": "blah",  # this is invalid
            "source_account": "raoV5dkC66XvGWjSzUhCUuuGM3YFTitMxT",
            "destination_account": "rJjusz1VauNA9XaHxJoiwHe38bmQFz1sUV",
            "destination_amount": "100",
        }
        with self.assertRaises(XRPLModelException) as e:
            PathFind(**path_find_dict)
        self.assertEqual(
            e.exception.args[0],
            str(
                {
                    "subcommand": (
                        "subcommand is blah, expected member of "
                        "<enum 'PathFindSubcommand'> enum"
                    )
                }
            ),
        )


class TestFromDict(TestCase):
    maxDiff = 2000

    def test_basic(self):
        amount = IssuedCurrencyAmount.from_dict(amount_dict)
        self.assertEqual(amount, IssuedCurrencyAmount(**amount_dict))

    def test_recursive_amount(self):
        check_create = CheckCreate.from_dict(check_create_dict)

        expected_dict = {
            **check_create_dict,
            "transaction_type": "CheckCreate",
            "flags": 0,
            "signing_pub_key": "",
        }
        self.assertEqual(expected_dict, check_create.to_dict())

    def test_recursive_currency(self):
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
            "api_version": _DEFAULT_API_VERSION,
        }
        self.assertEqual(expected_dict, book_offers.to_dict())

    def test_recursive_transaction(self):
        transaction = CheckCreate.from_dict(check_create_dict)
        sign_dict = {"secret": secret, "tx_json": transaction.to_xrpl()}
        sign = Sign.from_dict(sign_dict)

        expected_dict = {
            **sign_dict,
            "tx_json": transaction.to_xrpl(),
            "method": "sign",
            "fee_mult_max": 10,
            "fee_div_max": 1,
            "offline": False,
            "api_version": _DEFAULT_API_VERSION,
        }
        self.assertEqual(expected_dict, sign.to_dict())

    def test_recursive_transaction_tx_json(self):
        transaction = CheckCreate.from_dict(check_create_dict)
        sign_dict = {"secret": secret, "tx_json": transaction.to_xrpl()}
        sign = Sign.from_dict(sign_dict)

        expected_dict = {
            **sign_dict,
            "tx_json": transaction.to_xrpl(),
            "method": "sign",
            "fee_mult_max": 10,
            "fee_div_max": 1,
            "offline": False,
            "api_version": _DEFAULT_API_VERSION,
        }
        self.assertEqual(expected_dict, sign.to_dict())

    def test_signer(self):
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

    def test_trust_set(self):
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

    def test_list_of_lists(self):
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

    def test_any(self):
        account_channels_dict = {
            "account": "rH6ZiHU1PGamME2LvVTxrgvfjQpppWKGmr",
            "marker": "something",
        }
        expected = AccountChannels(**account_channels_dict)
        actual = AccountChannels.from_dict(account_channels_dict)
        self.assertEqual(actual, expected)

    def test_bad_str(self):
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

    def test_explicit_none(self):
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

    def test_with_str_enum_value(self):
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

    def test_bad_list(self):
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

    def test_multisign(self):
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

    def test_submit(self):
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

    def test_nonexistent_field(self):
        tx = {
            "account": "rH6ZiHU1PGamME2LvVTxrgvfjQpppWKGmr",
            "bad_field": "random",
            "flags": 131072,
            "limit_amount": {
                "currency": "USD",
                "issuer": "raoV5dkC66XvGWjSzUhCUuuGM3YFTitMxT",
                "value": "100",
            },
        }
        with self.assertRaises(XRPLModelException):
            TrustSet.from_dict(tx)

    def test_bad_literal(self):
        tx = {
            "account": issuer,
            "xchain_bridge": {
                "locking_chain_door": issuer,
                "locking_chain_issue": {"currency": "XRP"},
                "issuing_chain_door": issuer,
                "issuing_chain_issue": {"currency": "XRP"},
            },
            "public_key": "0342E083EA762D91D621714C394",
            "signature": "3044022053B26DAAC9C886192C95",
            "other_chain_source": issuer,
            "amount": amount_dict,
            "attestation_reward_account": issuer,
            "attestation_signer_account": issuer,
            "was_locking_chain_send": 2,  # supposed to be 0 or 1
            "xchain_account_create_count": 12,
            "destination": issuer,
            "signature_reward": "200",
        }
        with self.assertRaises(XRPLModelException):
            XChainAddAccountCreateAttestation.from_dict(tx)

    def test_good_literal(self):
        tx = {
            "account": issuer,
            "xchain_bridge": {
                "locking_chain_door": issuer,
                "locking_chain_issue": {"currency": "XRP"},
                "issuing_chain_door": issuer,
                "issuing_chain_issue": {"currency": "XRP"},
            },
            "public_key": "0342E083EA762D91D621714C394",
            "signature": "3044022053B26DAAC9C886192C95",
            "other_chain_source": issuer,
            "amount": "100",
            "attestation_reward_account": issuer,
            "attestation_signer_account": issuer,
            "was_locking_chain_send": 1,
            "xchain_account_create_count": 12,
            "destination": issuer,
            "signature_reward": "200",
        }
        expected_dict = {
            **tx,
            "xchain_bridge": XChainBridge.from_dict(tx["xchain_bridge"]),
        }
        expected = XChainAddAccountCreateAttestation(
            **expected_dict,
        )
        self.assertEqual(XChainAddAccountCreateAttestation.from_dict(tx), expected)

    def test_enum(self):
        path_find_dict = {
            "subcommand": "create",
            "source_account": "raoV5dkC66XvGWjSzUhCUuuGM3YFTitMxT",
            "destination_account": "rJjusz1VauNA9XaHxJoiwHe38bmQFz1sUV",
            "destination_amount": "100",
        }
        self.assertEqual(PathFind.from_dict(path_find_dict), PathFind(**path_find_dict))


class TestFromXrpl(TestCase):
    def test_from_xrpl(self):
        dirname = os.path.dirname(__file__)
        full_filename = "x-codec-fixtures.json"
        absolute_path = os.path.join(dirname, full_filename)
        with open(absolute_path) as fixtures_file:
            fixtures_json = json.load(fixtures_file)
            for test in fixtures_json["transactions"]:
                x_json = test["xjson"]
                r_json = test["rjson"]
                with self.subTest(json=x_json, use_json=False):
                    tx = Transaction.from_xrpl(x_json)
                    translated_tx = tx.to_xrpl()
                    self.assertEqual(x_json, translated_tx)
                with self.subTest(json=r_json, use_json=False):
                    tx = Transaction.from_xrpl(r_json)
                    translated_tx = tx.to_xrpl()
                    self.assertEqual(r_json, translated_tx)
                with self.subTest(json=r_json, use_json=True):
                    tx = Transaction.from_xrpl(json.dumps(r_json))
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

    def test_to_xrpl_auth_accounts(self):
        tx = AMMBid(
            account="r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ",
            asset=XRP(),
            asset2=IssuedCurrency(
                currency="ETH", issuer="rpGtkFRXhgVaBzC5XCR7gyE2AZN5SN3SEW"
            ),
            bid_min=IssuedCurrencyAmount(
                currency="5475B6C930B7BDD81CDA8FBA5CED962B11218E5A",
                issuer="r3628pXjRqfw5zfwGfhSusjZTvE3BoxEBw",
                value="25",
            ),
            bid_max=IssuedCurrencyAmount(
                currency="5475B6C930B7BDD81CDA8FBA5CED962B11218E5A",
                issuer="r3628pXjRqfw5zfwGfhSusjZTvE3BoxEBw",
                value="35",
            ),
            auth_accounts=[
                AuthAccount(account="rNZdsTBP5tH1M6GHC6bTreHAp6ouP8iZSh"),
                AuthAccount(account="rfpFv97Dwu89FTyUwPjtpZBbuZxTqqgTmH"),
                AuthAccount(account="rzzYHPGb8Pa64oqxCzmuffm122bitq3Vb"),
                AuthAccount(account="rhwxHxaHok86fe4LykBom1jSJ3RYQJs1h4"),
            ],
        )
        expected = {
            "Account": "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ",
            "Asset": {"currency": "XRP"},
            "Asset2": {
                "currency": "ETH",
                "issuer": "rpGtkFRXhgVaBzC5XCR7gyE2AZN5SN3SEW",
            },
            "BidMin": {
                "currency": "5475B6C930B7BDD81CDA8FBA5CED962B11218E5A",
                "issuer": "r3628pXjRqfw5zfwGfhSusjZTvE3BoxEBw",
                "value": "25",
            },
            "BidMax": {
                "currency": "5475B6C930B7BDD81CDA8FBA5CED962B11218E5A",
                "issuer": "r3628pXjRqfw5zfwGfhSusjZTvE3BoxEBw",
                "value": "35",
            },
            "AuthAccounts": [
                {
                    "AuthAccount": {
                        "Account": "rNZdsTBP5tH1M6GHC6bTreHAp6ouP8iZSh",
                    }
                },
                {
                    "AuthAccount": {
                        "Account": "rfpFv97Dwu89FTyUwPjtpZBbuZxTqqgTmH",
                    }
                },
                {
                    "AuthAccount": {
                        "Account": "rzzYHPGb8Pa64oqxCzmuffm122bitq3Vb",
                    }
                },
                {
                    "AuthAccount": {
                        "Account": "rhwxHxaHok86fe4LykBom1jSJ3RYQJs1h4",
                    }
                },
            ],
            "TransactionType": "AMMBid",
            "SigningPubKey": "",
            "Flags": 0,
        }
        self.assertEqual(tx.to_xrpl(), expected)

    def test_to_from_xrpl_xchain(self):
        tx_json = {
            "Account": account,
            "Amount": value,
            "XChainBridge": {
                "LockingChainDoor": "rGzx83BVoqTYbGn7tiVAnFw7cbxjin13jL",
                "LockingChainIssue": {"currency": "XRP"},
                "IssuingChainDoor": "r3kmLJN5D28dHuH8vZNUZpMC43pEHpaocV",
                "IssuingChainIssue": {"currency": "XRP"},
            },
            "Destination": destination,
            "TransactionType": "XChainClaim",
            "Flags": 0,
            "SigningPubKey": "",
            "XChainClaimID": 1,
        }
        tx_obj = XChainClaim(
            account=account,
            amount=value,
            xchain_bridge=XChainBridge(
                locking_chain_door="rGzx83BVoqTYbGn7tiVAnFw7cbxjin13jL",
                locking_chain_issue=XRP(),
                issuing_chain_door="r3kmLJN5D28dHuH8vZNUZpMC43pEHpaocV",
                issuing_chain_issue=XRP(),
            ),
            destination=destination,
            xchain_claim_id=1,
        )
        self.assertEqual(tx_obj.to_xrpl(), tx_json)
        self.assertEqual(Transaction.from_xrpl(tx_json), tx_obj)

    def test_request_input_from_xrpl_accepts_camel_case(self):
        # Note: BaseModel.from_xrpl and its overridden methods accept only camelCase or
        # PascalCase inputs (i.e. snake_case is not accepted)
        request = {
            "method": "submit",
            "tx_json": {
                "Account": "rnD6t3JF9RTG4VgNLoc4i44bsQLgJUSi6h",
                "transaction_type": "TrustSet",
                "Fee": "10",
                "Sequence": 17896798,
                "Flags": 131072,
                "signing_pub_key": "",
                "limit_amount": {
                    "currency": "USD",
                    "issuer": "rH5gvkKxGHrFAMAACeu9CB3FMu7pQ9jfZm",
                    "value": "10",
                },
            },
            "fail_hard": False,
        }

        with self.assertRaises(XRPLModelException):
            Request.from_xrpl(request)

    def test_transaction_input_from_xrpl_accepts_only_camel_case(self):
        # verify that Transaction.from_xrpl method does not accept snake_case JSON keys
        tx_snake_case_keys = {
            "Account": "rnoGkgSpt6AX1nQxZ2qVGx7Fgw6JEcoQas",
            "transaction_type": "TrustSet",
            "Fee": "10",
            "Sequence": 17892983,
            "Flags": 131072,
            "signing_pub_key": "",
            "limit_amount": {
                "currency": "USD",
                "issuer": "rBPvTKisx7UCGLDtiUZ6mDssXNREuVuL8Y",
                "value": "10",
            },
        }

        with self.assertRaises(XRPLModelException):
            Transaction.from_xrpl(tx_snake_case_keys)
