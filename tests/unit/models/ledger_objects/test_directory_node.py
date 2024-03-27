from unittest import TestCase

from xrpl.models.ledger_objects.directory_node import DirectoryNode
from xrpl.models.ledger_objects.ledger_object import LedgerObject


class TestDirectoryNode(TestCase):
    def test_directory_node(self):
        directory_node_json = {
            "ExchangeRate": "4F069BA8FF484000",
            "Flags": 0,
            "Indexes": [
                "AD7EAE148287EF12D213A251015F86E6D4BD34B3C4A0A1ED9A17198373F908AD"
            ],
            "LedgerEntryType": "DirectoryNode",
            "RootIndex": "1BBEF97EDE88D40CEE2ADE6FEF121166AFE80D99EBADB01A"
            "4F069BA8FF484000",
            "TakerGetsCurrency": "0000000000000000000000000000000000000000",
            "TakerGetsIssuer": "0000000000000000000000000000000000000000",
            "TakerPaysCurrency": "0000000000000000000000004A50590000000000",
            "TakerPaysIssuer": "5BBC0F22F61D9224A110650CFE21CC0C4BE13098",
            "index": "1BBEF97EDE88D40CEE2ADE6FEF121166AFE80D99EBADB01A4F069BA8FF484000",
        }
        actual = LedgerObject.from_xrpl(directory_node_json)
        expected = DirectoryNode(
            index="1BBEF97EDE88D40CEE2ADE6FEF121166AFE80D99EBADB01A4F069BA8FF484000",
            root_index="1BBEF97EDE88D40CEE2ADE6FEF121166A"
            "FE80D99EBADB01A4F069BA8FF484000",
            indexes=[
                "AD7EAE148287EF12D213A251015F86E6D4BD34B3C4A0A1ED9A17198373F908AD"
            ],
            exchange_rate="4F069BA8FF484000",
            taker_pays_currency="0000000000000000000000004A50590000000000",
            taker_pays_issuer="5BBC0F22F61D9224A110650CFE21CC0C4BE13098",
            taker_gets_currency="0000000000000000000000000000000000000000",
            taker_gets_issuer="0000000000000000000000000000000000000000",
        )
        self.assertEqual(actual, expected)
