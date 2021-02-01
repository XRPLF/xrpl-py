import unittest

# from xrpl.binary_codec.binary_wrappers.binary_parser import BinaryParser
from xrpl.binary_codec.types.serialized_transaction import SerializedTransaction


class TestSerializedTransaction(unittest.TestCase):
    def test_simple(self):
        json = {
            "Account": "raD5qJMAShLeHZXf9wjUmo6vRK4arj9cF3",
            "Fee": "10",
            "Flags": 0,
            "Sequence": 103929,
            "SigningPubKey": (
                "028472865AF4CB32AA285834B57576B7290AA8C31B459047DB27E16F418D6A7166"
            ),
            "TakerGets": {
                "currency": "ILS",
                "issuer": "rNPRNzBB92BVpAhhZr4iXDTveCgV5Pofm9",
                "value": "1694.768",
            },
            "TransactionType": "OfferCreate",
            "TxnSignature": (
                "304502202ABE08D5E78D1E74A4C18F2714F64E87B8BD57444AF"
                "A5733109EB3C077077520022100DB335EE97386E4C0591CAC02"
                "4D50E9230D8F171EEB901B5E5E4BD6D1E0AEF98C"
            ),
        }
        binary = (
            "120007220000000024000195F964400000170A53AC2065D5460561E"
            "C9DE000000000000000000000000000494C53000000000092D70596"
            "8936C419CE614BF264B5EEB1CEA47FF468400000000000000A73210"
            "28472865AF4CB32AA285834B57576B7290AA8C31B459047DB27E16F"
            "418D6A71667447304502202ABE08D5E78D1E74A4C18F2714F64E87B"
            "8BD57444AFA5733109EB3C077077520022100DB335EE97386E4C059"
            "1CAC024D50E9230D8F171EEB901B5E5E4BD6D1E0AEF98C811439408"
            "A69F0895E62149CFCC006FB89FA7D1E6E5D"
        )

        obj = SerializedTransaction.from_value(json)
        print(obj)
        print(binary)
