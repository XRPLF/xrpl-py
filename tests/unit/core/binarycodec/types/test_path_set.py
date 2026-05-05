from unittest import TestCase

from xrpl.core.binarycodec import XRPLBinaryCodecException
from xrpl.core.binarycodec.binary_wrappers.binary_parser import BinaryParser
from xrpl.core.binarycodec.types.account_id import AccountID
from xrpl.core.binarycodec.types.currency import Currency
from xrpl.core.binarycodec.types.path_set import PathSet

buffer = (
    "31585E1F3BD02A15D6"
    "185F8BB9B57CC60DEDDB37C10000000000000000000000004254430000000000"
    "585E1F3BD02A15D6185F8BB9B57CC60DEDDB37C131E4FE687C90257D3D2D694C"
    "8531CDEECBE84F33670000000000000000000000004254430000000000E4FE68"
    "7C90257D3D2D694C8531CDEECBE84F3367310A20B3C85F482532A9578DBB3950"
    "B85CA06594D100000000000000000000000042544300000000000A20B3C85F48"
    "2532A9578DBB3950B85CA06594D1300000000000000000000000005553440000"
    "0000000A20B3C85F482532A9578DBB3950B85CA06594D1FF31585E1F3BD02A15"
    "D6185F8BB9B57CC60DEDDB37C100000000000000000000000042544300000000"
    "00585E1F3BD02A15D6185F8BB9B57CC60DEDDB37C131E4FE687C90257D3D2D69"
    "4C8531CDEECBE84F33670000000000000000000000004254430000000000E4FE"
    "687C90257D3D2D694C8531CDEECBE84F33673115036E2D3F5437A83E5AC3CAEE"
    "34FF2C21DEB618000000000000000000000000425443000000000015036E2D3F"
    "5437A83E5AC3CAEE34FF2C21DEB6183000000000000000000000000055534400"
    "000000000A20B3C85F482532A9578DBB3950B85CA06594D1FF31585E1F3BD02A"
    "15D6185F8BB9B57CC60DEDDB37C1000000000000000000000000425443000000"
    "0000585E1F3BD02A15D6185F8BB9B57CC60DEDDB37C13157180C769B66D942EE"
    "69E6DCC940CA48D82337AD000000000000000000000000425443000000000057"
    "180C769B66D942EE69E6DCC940CA48D82337AD10000000000000000000000000"
    "00000000000000003000000000000000000000000055534400000000000A20B3"
    "C85F482532A9578DBB3950B85CA06594D100"
)

expected_json = [
    [
        {
            "account": "r9hEDb4xBGRfBCcX3E4FirDWQBAYtpxC8K",
            "currency": "BTC",
            "issuer": "r9hEDb4xBGRfBCcX3E4FirDWQBAYtpxC8K",
        },
        {
            "account": "rM1oqKtfh1zgjdAgbFmaRm3btfGBX25xVo",
            "currency": "BTC",
            "issuer": "rM1oqKtfh1zgjdAgbFmaRm3btfGBX25xVo",
        },
        {
            "account": "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
            "currency": "BTC",
            "issuer": "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
        },
        {
            "currency": "USD",
            "issuer": "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
        },
    ],
    [
        {
            "account": "r9hEDb4xBGRfBCcX3E4FirDWQBAYtpxC8K",
            "currency": "BTC",
            "issuer": "r9hEDb4xBGRfBCcX3E4FirDWQBAYtpxC8K",
        },
        {
            "account": "rM1oqKtfh1zgjdAgbFmaRm3btfGBX25xVo",
            "currency": "BTC",
            "issuer": "rM1oqKtfh1zgjdAgbFmaRm3btfGBX25xVo",
        },
        {
            "account": "rpvfJ4mR6QQAeogpXEKnuyGBx8mYCSnYZi",
            "currency": "BTC",
            "issuer": "rpvfJ4mR6QQAeogpXEKnuyGBx8mYCSnYZi",
        },
        {
            "currency": "USD",
            "issuer": "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
        },
    ],
    [
        {
            "account": "r9hEDb4xBGRfBCcX3E4FirDWQBAYtpxC8K",
            "currency": "BTC",
            "issuer": "r9hEDb4xBGRfBCcX3E4FirDWQBAYtpxC8K",
        },
        {
            "account": "r3AWbdp2jQLXLywJypdoNwVSvr81xs3uhn",
            "currency": "BTC",
            "issuer": "r3AWbdp2jQLXLywJypdoNwVSvr81xs3uhn",
        },
        {"currency": "XRP"},
        {
            "currency": "USD",
            "issuer": "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
        },
    ],
]


class TestPathSet(TestCase):
    def test_from_value(self):
        pathset = PathSet.from_value(expected_json)
        self.assertEqual(buffer, str(pathset))

    def test_from_value_to_json(self):
        pathset = PathSet.from_value(expected_json)
        self.assertEqual(pathset.to_json(), expected_json)

    def test_from_parser_to_json(self):
        parser = BinaryParser(buffer)
        pathset = PathSet.from_parser(parser)
        self.assertEqual(pathset.to_json(), expected_json)

    def test_raises_invalid_value_type(self):
        invalid_value = 1
        self.assertRaises(XRPLBinaryCodecException, PathSet.from_value, invalid_value)

    # ── MPT PathSet serialization tests ──
    #
    # PathSet binary format reference (from rippled STPathSet.cpp):
    #
    # Each path step starts with a 1-byte type flag bitmask:
    #   0x01 = account    (followed by 20-byte AccountID)
    #   0x10 = currency   (followed by 20-byte Currency)
    #   0x20 = issuer     (followed by 20-byte AccountID)
    #   0x40 = MPT        (followed by 24-byte MPTID)
    #
    # Special marker bytes:
    #   0xFF = path boundary (separates alternative paths within a PathSet)
    #   0x00 = end of PathSet (terminates the entire PathSet)
    #
    # Currency (0x10) and MPT (0x40) are mutually exclusive within a
    # single path step — a step cannot carry both flags.

    def test_one_path_with_one_mpt_hop(self):
        mpt_issuance_id = "00000001B5F762798A53D543A014CAF8B297CFF8F2F937E8"
        path = [[{"mpt_issuance_id": mpt_issuance_id}]]

        pathset = PathSet.from_value(path)
        # "40"               → type byte: MPT flag (0x40)
        # mpt_issuance_id    → raw 24-byte MPTID
        # "00"               → end of PathSet
        expected_hex = "40" + mpt_issuance_id + "00"
        self.assertEqual(str(pathset).upper(), expected_hex)

        # round-trip JSON equivalence
        self.assertEqual(pathset.to_json(), path)

        # deserialization via BinaryParser
        parser = BinaryParser(expected_hex)
        self.assertEqual(str(PathSet.from_parser(parser)), str(pathset))

    def test_two_paths_with_mpt_hops(self):
        mpt_id_1 = "00000001B5F762798A53D543A014CAF8B297CFF8F2F937E8"
        mpt_id_2 = "000004C463C52827307480341125DA0577DEFC38405B0E3E"
        path = [
            [{"mpt_issuance_id": mpt_id_1}],
            [{"mpt_issuance_id": mpt_id_2}],
        ]

        pathset = PathSet.from_value(path)
        # "40" + mpt_id_1    → first path: one MPT hop
        # "FF"               → path boundary separating alternative paths
        # "40" + mpt_id_2    → second path: one MPT hop
        # "00"               → end of PathSet
        expected_hex = "40" + mpt_id_1 + "FF" + "40" + mpt_id_2 + "00"
        self.assertEqual(str(pathset).upper(), expected_hex)

        self.assertEqual(pathset.to_json(), path)

        parser = BinaryParser(expected_hex)
        self.assertEqual(str(PathSet.from_parser(parser)), str(pathset))

    def test_path_with_mpt_and_currency_path_elements(self):
        """One path with two distinct steps: an MPT hop followed by a Currency hop."""
        mpt_issuance_id = "00000001B5F762798A53D543A014CAF8B297CFF8F2F937E8"
        currency_code = "ABC"
        path = [
            [
                {"mpt_issuance_id": mpt_issuance_id},
                {"currency": currency_code},
            ]
        ]

        pathset = PathSet.from_value(path)
        currency_hex = str(Currency.from_value(currency_code)).upper()
        # "40" + mpt_id      → first step: MPT hop (0x40 type flag)
        # "10" + currency_hex → second step: Currency hop (0x10 type flag)
        # "00"               → end of PathSet
        expected_hex = "40" + mpt_issuance_id + "10" + currency_hex + "00"
        self.assertEqual(str(pathset).upper(), expected_hex)

        self.assertEqual(pathset.to_json(), path)

        parser = BinaryParser(expected_hex)
        self.assertEqual(str(PathSet.from_parser(parser)), str(pathset))

    def test_path_with_mpt_and_issuer_path_elements(self):
        """One path with two distinct steps: an MPT hop followed by an Issuer hop."""
        mpt_issuance_id = "00000001B5F762798A53D543A014CAF8B297CFF8F2F937E8"
        issuer_account = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
        path = [
            [
                {"mpt_issuance_id": mpt_issuance_id},
                {"issuer": issuer_account},
            ]
        ]

        pathset = PathSet.from_value(path)
        issuer_hex = str(AccountID.from_value(issuer_account)).upper()
        # "40" + mpt_id     → first step: MPT hop (0x40 type flag)
        # "20" + issuer_hex  → second step: Issuer hop (0x20 type flag)
        # "00"               → end of PathSet
        expected_hex = "40" + mpt_issuance_id + "20" + issuer_hex + "00"
        self.assertEqual(str(pathset).upper(), expected_hex)

        self.assertEqual(pathset.to_json(), path)

        parser = BinaryParser(expected_hex)
        self.assertEqual(str(PathSet.from_parser(parser)), str(pathset))

    def test_currency_and_mpt_mutually_exclusive_in_serialization(self):
        """Providing both currency and mpt_issuance_id in a single step must raise."""
        path = [
            [
                {
                    "currency": "ABC",
                    "mpt_issuance_id": "00000001B5F762798A53"
                    "D543A014CAF8B297CFF8F2F937E8",
                }
            ]
        ]
        self.assertRaises(XRPLBinaryCodecException, PathSet.from_value, path)

    def test_currency_and_mpt_mutually_exclusive_in_deserialization(self):
        """A type byte with both Currency (0x10) and MPT (0x40) flags must raise."""
        # "50" = 0x10 | 0x40 — an invalid combination
        currency_hex = str(Currency.from_value("ABC")).upper()
        mpt_hex = "00000001B5F762798A53D543A014CAF8B297CFF8F2F937E8"
        invalid_hex = "50" + currency_hex + mpt_hex + "00"

        parser = BinaryParser(invalid_hex)
        self.assertRaises(XRPLBinaryCodecException, PathSet.from_parser, parser)

    def test_account_and_mpt_mutually_exclusive_in_serialization(self):
        """Providing both account and mpt_issuance_id in a single step must raise."""
        account = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
        mpt_id = "00000001B5F762798A53D543A014CAF8B297CFF8F2F937E8"
        path = [[{"account": account, "mpt_issuance_id": mpt_id}]]
        self.assertRaises(XRPLBinaryCodecException, PathSet.from_value, path)

    def test_account_and_mpt_mutually_exclusive_in_deserialization(self):
        """A type byte with both Account (0x01) and MPT (0x40) flags must raise."""
        # "41" = 0x01 | 0x40 — an invalid combination
        account = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
        account_hex = str(AccountID.from_value(account)).upper()
        mpt_hex = "00000001B5F762798A53D543A014CAF8B297CFF8F2F937E8"
        invalid_hex = "41" + account_hex + mpt_hex + "00"

        parser = BinaryParser(invalid_hex)
        self.assertRaises(XRPLBinaryCodecException, PathSet.from_parser, parser)
