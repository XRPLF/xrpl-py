from unittest import TestCase

from xrpl.core.binarycodec import XRPLBinaryCodecException
from xrpl.core.binarycodec.binary_wrappers.binary_parser import BinaryParser
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


_MPT_ID = "00000003430427B80BD2D09D36B70B969E12801065F22308"
_MPT_ISSUER = "rffMEZLzDQPNU6VYbWNkgQBtMz6gCYnMAG"
_MPT_ISSUER_HEX = "430427B80BD2D09D36B70B969E12801065F22308"
_USD_HEX = "0000000000000000000000005553440000000000"
_IOU_ISSUER = "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B"
_IOU_ISSUER_HEX = "0A20B3C85F482532A9578DBB3950B85CA06594D1"

# An MPT step has type 0x40 and a 24-byte MPTokenIssuanceID in place of the
# currency. rippled's pathfinder also sets the issuer (0x40 | 0x20).
mpt_json = [
    [{"currency": "USD", "issuer": _IOU_ISSUER}, {"mpt_issuance_id": _MPT_ID}],
    [{"mpt_issuance_id": _MPT_ID, "issuer": _MPT_ISSUER}],
]
mpt_buffer = (
    "30"
    + _USD_HEX
    + _IOU_ISSUER_HEX
    + "40"
    + _MPT_ID
    + "FF"
    + "60"
    + _MPT_ID
    + _MPT_ISSUER_HEX
    + "00"
)


class TestPathSetMPT(TestCase):
    def test_from_value(self):
        self.assertEqual(str(PathSet.from_value(mpt_json)), mpt_buffer)

    def test_from_parser_to_json(self):
        pathset = PathSet.from_parser(BinaryParser(mpt_buffer))
        self.assertEqual(pathset.to_json(), mpt_json)

    def test_mpt_as_first_step(self):
        pathset = PathSet.from_value([[{"mpt_issuance_id": _MPT_ID}]])
        self.assertEqual(str(pathset), "40" + _MPT_ID + "00")

    def test_lowercase_mpt_issuance_id_is_normalized(self):
        pathset = PathSet.from_value([[{"mpt_issuance_id": _MPT_ID.lower()}]])
        self.assertEqual(pathset.to_json(), [[{"mpt_issuance_id": _MPT_ID}]])

    def test_account_with_mpt(self):
        # rippled accepts this combination, so the codec does too.
        value = [[{"account": _IOU_ISSUER, "mpt_issuance_id": _MPT_ID}]]
        pathset = PathSet.from_value(value)
        self.assertEqual(str(pathset), "41" + _IOU_ISSUER_HEX + _MPT_ID + "00")
        self.assertEqual(pathset.to_json(), value)

    def test_raises_currency_and_mpt(self):
        value = [[{"currency": "USD", "mpt_issuance_id": _MPT_ID}]]
        with self.assertRaises(XRPLBinaryCodecException):
            PathSet.from_value(value)

    def test_raises_step_without_fields(self):
        # The empty type byte would otherwise end the PathSet early.
        value = [[{"currency": "USD", "issuer": _IOU_ISSUER}, {"type": 1}]]
        with self.assertRaises(XRPLBinaryCodecException):
            PathSet.from_value(value)

    def test_from_parser_raises_currency_and_mpt(self):
        parser = BinaryParser("50" + _USD_HEX + _MPT_ID + "00")
        with self.assertRaises(XRPLBinaryCodecException):
            PathSet.from_parser(parser)

    def test_from_parser_raises_unknown_type_bits(self):
        with self.assertRaises(XRPLBinaryCodecException):
            PathSet.from_parser(BinaryParser("02" + _MPT_ID + "00"))
