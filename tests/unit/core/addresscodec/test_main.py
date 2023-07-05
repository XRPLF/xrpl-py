import asyncio
from unittest import TestCase

from tests.unit.core.addresscodec.test_main_test_cases import test_cases
from xrpl.asyncio.transaction.main import _calculate_fee_per_transaction_type
from xrpl.core import addresscodec
from xrpl.core.addresscodec.main import MAX_32_BIT_UNSIGNED_INT
from xrpl.models.amounts.issued_currency_amount import IssuedCurrencyAmount
from xrpl.models.transactions.payment import Payment


class TestMain(TestCase):
    def test_classic_address_to_xaddress(self):
        for test_case in test_cases:
            (
                classic_address,
                tag,
                expected_main_xaddress,
                expected_test_xaddress,
            ) = test_case

            # test
            xaddress = addresscodec.classic_address_to_xaddress(
                classic_address, tag, True
            )
            self.assertEqual(xaddress, expected_test_xaddress)

            # main
            xaddress = addresscodec.classic_address_to_xaddress(
                classic_address, tag, False
            )
            self.assertEqual(xaddress, expected_main_xaddress)

    def test_xaddress_to_classic_address(self):
        for test_case in test_cases:
            (
                expected_classic_address,
                expected_tag,
                main_xaddress,
                test_xaddress,
            ) = test_case

            # test
            classic_address, tag, is_test = addresscodec.xaddress_to_classic_address(
                test_xaddress
            )
            self.assertEqual(classic_address, expected_classic_address)
            self.assertEqual(tag, expected_tag)
            self.assertTrue(is_test)

            # main
            classic_address, tag, is_test = addresscodec.xaddress_to_classic_address(
                main_xaddress
            )
            self.assertEqual(classic_address, expected_classic_address)
            self.assertEqual(tag, expected_tag)
            self.assertFalse(is_test)

    def test_classic_address_to_xaddress_invalid_tag(self):
        classic_address = "rGWrZyQqhTp9Xu7G5Pkayo7bXjH4k4QYpf"
        tag = MAX_32_BIT_UNSIGNED_INT + 1

        self.assertRaises(
            addresscodec.XRPLAddressCodecException,
            addresscodec.classic_address_to_xaddress,
            classic_address,
            tag,
            True,
        )

        self.assertRaises(
            addresscodec.XRPLAddressCodecException,
            addresscodec.classic_address_to_xaddress,
            classic_address,
            tag,
            False,
        )

    def test_classic_address_to_xaddress_bad_classic_address(self):
        classic_address = "r"

        self.assertRaises(
            ValueError,
            addresscodec.classic_address_to_xaddress,
            classic_address,
            None,
            True,
        )

        self.assertRaises(
            ValueError,
            addresscodec.classic_address_to_xaddress,
            classic_address,
            None,
            False,
        )

    def test_ensure_classic_address(self):
        for test_case in test_cases:
            (
                expected_classic_address,
                tag,
                main_xaddress,
                test_xaddress,
            ) = test_case

            # classic address
            classic_address = addresscodec.ensure_classic_address(
                expected_classic_address
            )
            self.assertEqual(classic_address, expected_classic_address)

            # tagged xaddress
            if tag is not None:
                self.assertRaises(
                    addresscodec.XRPLAddressCodecException,
                    addresscodec.ensure_classic_address,
                    main_xaddress,
                )
                self.assertRaises(
                    addresscodec.XRPLAddressCodecException,
                    addresscodec.ensure_classic_address,
                    test_xaddress,
                )
            else:
                # main xaddress
                classic_address = addresscodec.ensure_classic_address(main_xaddress)
                self.assertEqual(classic_address, expected_classic_address)

                # test xaddress
                classic_address = addresscodec.ensure_classic_address(test_xaddress)
                self.assertEqual(classic_address, expected_classic_address)

    def test_is_valid_classic_address_secp256k1(self):
        classic_address = "rU6K7V3Po4snVhBBaU29sesqs2qTQJWDw1"

        result = addresscodec.is_valid_classic_address(classic_address)
        self.assertTrue(result)

    def test_is_valid_classic_address_ed25519(self):
        classic_address = "rLUEXYuLiQptky37CqLcm9USQpPiz5rkpD"

        result = addresscodec.is_valid_classic_address(classic_address)
        self.assertTrue(result)

    def test_is_valid_classic_address_invalid(self):
        classic_address = "rU6K7V3Po4snVhBBaU29sesqs2qTQJWDw2"

        result = addresscodec.is_valid_classic_address(classic_address)
        self.assertFalse(result)

    def test_is_valid_classic_address_empty(self):
        classic_address = ""

        result = addresscodec.is_valid_classic_address(classic_address)
        self.assertFalse(result)

    def test_is_valid_xaddress_valid(self):
        xaddress = "X7AcgcsBL6XDcUb289X4mJ8djcdyKaB5hJDWMArnXr61cqZ"

        result = addresscodec.is_valid_xaddress(xaddress)
        self.assertTrue(result)

    def test_is_valid_xaddress_invalid(self):
        xaddress = "XVLhHMPHU98es4dbozjVtdWzVrDjtV18pX8zeUygYrCgrPh"

        result = addresscodec.is_valid_xaddress(xaddress)
        self.assertFalse(result)

    def test_is_valid_xaddress_empty(self):
        xaddress = ""

        result = addresscodec.is_valid_xaddress(xaddress)
        self.assertFalse(result)

    def test_basic_calculate_fee_per_transaction_type_offline(self):
        fee = asyncio.run(
            _calculate_fee_per_transaction_type(
                Payment(
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
                )
            )
        )
        self.assertEqual(fee, "10")
