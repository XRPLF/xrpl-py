from unittest import TestCase

from xrpl.constants import CryptoAlgorithm, XRPLException
from xrpl.core.binarycodec.main import decode
from xrpl.models.transactions import Batch
from xrpl.models.transactions.batch import BatchSigner
from xrpl.models.transactions.transaction import Transaction
from xrpl.transaction.batch_signers import (
    combine_batch_signers,
    sign_multiaccount_batch,
)
from xrpl.wallet import Wallet

secp_wallet = Wallet.from_seed(
    "spkcsko6Ag3RbCSVXV2FJ8Pd4Zac1",
    algorithm=CryptoAlgorithm.SECP256K1,
)
ed_wallet = Wallet.from_seed(
    "spkcsko6Ag3RbCSVXV2FJ8Pd4Zac1",
    algorithm=CryptoAlgorithm.ED25519,
)
submit_wallet = Wallet.from_seed(
    "sEd7HmQFsoyj5TAm6d98gytM9LJA1MF",
    algorithm=CryptoAlgorithm.ED25519,
)
other_wallet = Wallet.create()


class TestSignMultiAccountBatch(TestCase):
    batch_tx = Batch.from_xrpl(
        {
            "Account": "rJCxK2hX9tDMzbnn3cg1GU2g19Kfmhzxkp",
            "Flags": 1,
            "RawTransactions": [
                {
                    "RawTransaction": {
                        "Account": "rJy554HmWFFJQGnRfZuoo8nV97XSMq77h7",
                        "Amount": "5000000",
                        "BatchTxn": {
                            "BatchIndex": 1,
                            "OuterAccount": "rJCxK2hX9tDMzbnn3cg1GU2g19Kfmhzxkp",
                            "Sequence": 215,
                        },
                        "Destination": "rPMh7Pi9ct699iZUTWaytJUoHcJ7cgyziK",
                        "Fee": "0",
                        "NetworkID": 21336,
                        "Sequence": 0,
                        "SigningPubKey": "",
                        "TransactionType": "Payment",
                    },
                },
                {
                    "RawTransaction": {
                        "Account": "rPMh7Pi9ct699iZUTWaytJUoHcJ7cgyziK",
                        "Amount": "1000000",
                        "BatchTxn": {
                            "BatchIndex": 0,
                            "OuterAccount": "rJCxK2hX9tDMzbnn3cg1GU2g19Kfmhzxkp",
                            "Sequence": 470,
                        },
                        "Destination": "rJCxK2hX9tDMzbnn3cg1GU2g19Kfmhzxkp",
                        "Fee": "0",
                        "NetworkID": 21336,
                        "Sequence": 0,
                        "SigningPubKey": "",
                        "TransactionType": "Payment",
                    },
                },
            ],
            "TransactionType": "Batch",
            "TxIDs": [
                "ABE4871E9083DF66727045D49DEEDD3A6F166EB7F8D1E92FE868F02E76B2C5CA",
                "795AAC88B59E95C3497609749127E69F12958BC016C600C770AEEB1474C840B4",
            ],
        }
    )

    def test_secp_wallet(self):
        result = sign_multiaccount_batch(secp_wallet, self.batch_tx)
        expected = [
            BatchSigner(
                account="rPMh7Pi9ct699iZUTWaytJUoHcJ7cgyziK",
                signing_pub_key=(
                    "02691AC5AE1C4C333AE5DF8A93BDC495F0EEBFC6DB0DA7EB6EF80"
                    "8F3AFC006E3FE"
                ),
                txn_signature=(
                    "30450221008E595499C334127A23190F61FB9ADD8B8C501D543E379"
                    "45B11FABB66B097A6130220138C908E8C4929B47E994A46D611FAC1"
                    "7AB295CFB8D9E0828B32F2947B97394B"
                ),
            )
        ]

        self.assertIsNotNone(result.batch_signers)
        self.assertEqual(result.batch_signers, expected)

    def test_ed_wallet(self):
        result = sign_multiaccount_batch(ed_wallet, self.batch_tx)
        expected = [
            BatchSigner(
                account="rJy554HmWFFJQGnRfZuoo8nV97XSMq77h7",
                signing_pub_key=(
                    "ED3CC3D14FD80C213BC92A98AFE13A405A030F845EDCFD5E39528"
                    "6A6E9E62BA638"
                ),
                txn_signature=(
                    "E3337EE8C746523B5F96BEBE1190164B8B384EE2DC99F327D95ABC1"
                    "4E27F3AE16CC00DA7D61FC535DBFF0ADA3AF06394F8A703EE952A14"
                    "1BD871B75166C5CD0A"
                ),
            )
        ]

        self.assertIsNotNone(result.batch_signers)
        self.assertEqual(result.batch_signers, expected)

    def test_not_included_account(self):
        with self.assertRaises(XRPLException):
            sign_multiaccount_batch(other_wallet, self.batch_tx)


class TestCombineBatchSigners(TestCase):
    batch_tx = Batch.from_xrpl(
        {
            "Account": "rJCxK2hX9tDMzbnn3cg1GU2g19Kfmhzxkp",
            "Flags": 1,
            "LastLedgerSequence": 14973,
            "NetworkID": 21336,
            "RawTransactions": [
                {
                    "RawTransaction": {
                        "Account": "rJy554HmWFFJQGnRfZuoo8nV97XSMq77h7",
                        "Amount": "5000000",
                        "BatchTxn": {
                            "BatchIndex": 1,
                            "OuterAccount": "rJCxK2hX9tDMzbnn3cg1GU2g19Kfmhzxkp",
                            "Sequence": 215,
                        },
                        "Destination": "rPMh7Pi9ct699iZUTWaytJUoHcJ7cgyziK",
                        "Fee": "0",
                        "NetworkID": 21336,
                        "Sequence": 0,
                        "SigningPubKey": "",
                        "TransactionType": "Payment",
                    },
                },
                {
                    "RawTransaction": {
                        "Account": "rPMh7Pi9ct699iZUTWaytJUoHcJ7cgyziK",
                        "Amount": "1000000",
                        "BatchTxn": {
                            "BatchIndex": 0,
                            "OuterAccount": "rJCxK2hX9tDMzbnn3cg1GU2g19Kfmhzxkp",
                            "Sequence": 470,
                        },
                        "Destination": "rJCxK2hX9tDMzbnn3cg1GU2g19Kfmhzxkp",
                        "Fee": "0",
                        "NetworkID": 21336,
                        "Sequence": 0,
                        "SigningPubKey": "",
                        "TransactionType": "Payment",
                    },
                },
            ],
            "Sequence": 215,
            "TransactionType": "Batch",
            "TxIDs": [
                "ABE4871E9083DF66727045D49DEEDD3A6F166EB7F8D1E92FE868F02E76B2C5CA",
                "795AAC88B59E95C3497609749127E69F12958BC016C600C770AEEB1474C840B4",
            ],
        }
    )
    tx1 = sign_multiaccount_batch(ed_wallet, batch_tx)
    tx2 = sign_multiaccount_batch(secp_wallet, batch_tx)
    expected_valid = tx1.to_xrpl().get("BatchSigners", []) + tx2.to_xrpl().get(
        "BatchSigners", []
    )

    def test_valid(self):
        result = combine_batch_signers([self.tx1, self.tx2])
        self.assertEqual(decode(result)["BatchSigners"], self.expected_valid)

    def test_valid_serialized(self):
        result = combine_batch_signers([self.tx1.blob(), self.tx2.blob()])
        self.assertEqual(decode(result)["BatchSigners"], self.expected_valid)

    def test_valid_sorted(self):
        result = combine_batch_signers([self.tx2, self.tx1])
        self.assertEqual(decode(result)["BatchSigners"], self.expected_valid)

    def test_remove_submitter_signature(self):
        tx = Transaction.from_xrpl(
            {
                "Account": "rJCxK2hX9tDMzbnn3cg1GU2g19Kfmhzxkp",
                "Amount": "1000000",
                "BatchTxn": {
                    "BatchIndex": 0,
                    "OuterAccount": "rJCxK2hX9tDMzbnn3cg1GU2g19Kfmhzxkp",
                    "Sequence": 470,
                },
                "Destination": "rPMh7Pi9ct699iZUTWaytJUoHcJ7cgyziK",
                "Fee": "0",
                "NetworkID": 21336,
                "Sequence": 0,
                "SigningPubKey": "",
                "TransactionType": "Payment",
            }
        )
        original_dict = self.batch_tx.to_xrpl()
        original_dict["RawTransactions"].append({"RawTransaction": tx.to_xrpl()})
        original_dict["TxIDs"].append(tx.get_hash())

        batch_tx = Batch.from_xrpl(original_dict)
        tx1 = sign_multiaccount_batch(ed_wallet, batch_tx)
        tx2 = sign_multiaccount_batch(secp_wallet, batch_tx)
        tx3 = sign_multiaccount_batch(submit_wallet, batch_tx)

        result = combine_batch_signers([tx1, tx2, tx3])
        expected_valid = tx1.to_xrpl().get("BatchSigners", []) + tx2.to_xrpl().get(
            "BatchSigners", []
        )
        self.assertEqual(decode(result)["BatchSigners"], expected_valid)
