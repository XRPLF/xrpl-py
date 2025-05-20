from unittest import TestCase

from xrpl.core.binarycodec.binary_wrappers.binary_parser import BinaryParser
from xrpl.core.binarycodec.types.st_object import STObject

expected_json = {
    "Account": "raD5qJMAShLeHZXf9wjUmo6vRK4arj9cF3",
    "Fee": "10",
    "Flags": 0,
    "Sequence": 103929,
    "SigningPubKey": (
        "028472865AF4CB32AA285834B57576B7290AA8C31B459047DB27E16F418D6A7166"
    ),
    "TakerGets": {
        "value": "1694.768",
        "currency": "ILS",
        "issuer": "rNPRNzBB92BVpAhhZr4iXDTveCgV5Pofm9",
    },
    "TakerPays": "98957503520",
    "TransactionType": "OfferCreate",
    "TxnSignature": (
        "304502202ABE08D5E78D1E74A4C18F2714F64E87B8BD57444AFA5733"
        "109EB3C077077520022100DB335EE97386E4C0591CAC024D50E9230D8"
        "F171EEB901B5E5E4BD6D1E0AEF98C"
    ),
}

buffer = (
    "120007220000000024000195F964400000170A53AC2065D5460561E"
    "C9DE000000000000000000000000000494C53000000000092D70596"
    "8936C419CE614BF264B5EEB1CEA47FF468400000000000000A73210"
    "28472865AF4CB32AA285834B57576B7290AA8C31B459047DB27E16F"
    "418D6A71667447304502202ABE08D5E78D1E74A4C18F2714F64E87B"
    "8BD57444AFA5733109EB3C077077520022100DB335EE97386E4C059"
    "1CAC024D50E9230D8F171EEB901B5E5E4BD6D1E0AEF98C811439408"
    "A69F0895E62149CFCC006FB89FA7D1E6E5D"
)


class TestSTObject(TestCase):
    maxDiff = 1000

    def test_from_value(self):
        transaction = STObject.from_value(expected_json)
        self.assertEqual(buffer, str(transaction).upper())

    def test_from_value_to_json(self):
        transaction = STObject.from_value(expected_json)
        self.assertEqual(transaction.to_json(), expected_json)

    def test_from_parser_to_json(self):
        parser = BinaryParser(buffer)
        transaction = STObject.from_parser(parser)
        self.assertEqual(transaction.to_json(), expected_json)
