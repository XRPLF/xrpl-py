import unittest

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.nftoken_create_offer import NFTokenCreateOffer
from xrpl.models.transactions.nftoken_create_offer import NFTokenCreateOfferFlag


class TestNFTokenCreateOffer(unittest.TestCase):
    def test_tx_invalid_missing_required_param_nftoken_id(self):
        with self.assertRaises(XRPLModelException) as err:
            NFTokenCreateOffer(
                account="rJ73aumLPTQQmy5wnGhvrogqf5DDhjuzc9",
                amount="12345",
                destination="AAAAA",
                expiration=5,
                flags=NFTokenCreateOfferFlag.TF_SELL_NFTOKEN,
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_duplicate_destination_and_account(self):
        with self.assertRaises(XRPLModelException) as err:
            NFTokenCreateOffer(
                account="rJ73aumLPTQQmy5wnGhvrogqf5DDhjuzc9",
                amount="12345",
                destination="rJ73aumLPTQQmy5wnGhvrogqf5DDhjuzc9",
                expiration=5,
                flags=NFTokenCreateOfferFlag.TF_SELL_NFTOKEN,
                nftoken_id="AAAAA",
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_present_owner_on_present_tf_sell_nftoken(self):
        with self.assertRaises(XRPLModelException) as err:
            NFTokenCreateOffer(
                account="rJ73aumLPTQQmy5wnGhvrogqf5DDhjuzc9",
                amount="12345",
                destination="AAAAA",
                expiration=5,
                flags=NFTokenCreateOfferFlag.TF_SELL_NFTOKEN,
                nftoken_id="AAAAA",
                owner="AAAAA",
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            NFTokenCreateOffer(
                account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE",
                amount="12345",
                destination="AAAAA",
                expiration=5,
                flags=NFTokenCreateOfferFlag.TF_SELL_NFTOKEN,
                nftoken_id="AAAAA",
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_valid_transaction(self):
        tx = NFTokenCreateOffer(
            account="rJ73aumLPTQQmy5wnGhvrogqf5DDhjuzc9",
            amount="12345",
            destination="AAAAA",
            expiration=5,
            flags=NFTokenCreateOfferFlag.TF_SELL_NFTOKEN,
            nftoken_id="AAAAA",
        )
        self.assertTrue(tx.is_valid())
