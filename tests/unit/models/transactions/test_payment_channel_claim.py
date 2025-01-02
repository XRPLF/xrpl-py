from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import PaymentChannelClaim
from xrpl.models.utils import MAX_CREDENTIAL_ARRAY_LENGTH

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"


class TestPaymentChannelClaim(TestCase):
    def test_valid(self):
        tx = PaymentChannelClaim(
            account=_ACCOUNT,
            channel="5DB01B7FFED6B67E6B0414DED11E051D2EE2B7619CE0EAA6286D67A3A4D5BDB3",
            balance="1000",
            signature="304402204EF0AFB78AC23ED1C472E74F4299C0C21F1B21D07EFC0A3838A420F"
            "76D783A400220154FB11B6F54320666E4C36CA7F686C16A3A0456800BBC43746F34AF5029"
            "0064",
            public_key="023693F15967AE357D0327974AD46FE3C127113B1110D6044FD41E723689F8"
            "1CC6",
            credential_ids=[
                "EA85602C1B41F6F1F5E83C0E6B87142FB8957BD209469E4CC347BA2D0C26F66A",
                "F9F89FBB1426210D58D6A06E5EEF1783D6A90EE403B79AEDF0FED36A6DE238D2",
                "5328F2D1D6EBBC6093DC10F1EA3DD630666F5B2491EB9BDD7DF9A6C45AC12C46",
            ],
        )
        self.assertTrue(tx.is_valid())

    def test_creds_list_too_long(self):
        with self.assertRaises(XRPLModelException) as err:
            PaymentChannelClaim(
                account=_ACCOUNT,
                channel="5DB01B7FFED6B67E6B0414DED11E051D2EE2B7619CE0EAA6286D67A3A4D5B"
                "DB3",
                balance="1000",
                signature="304402204EF0AFB78AC23ED1C472E74F4299C0C21F1B21D07EFC0A3838A4"
                "20F76D783A400220154FB11B6F54320666E4C36CA7F686C16A3A0456800BBC43746F34"
                "AF50290064",
                public_key="023693F15967AE357D0327974AD46FE3C127113B1110D6044FD41E72368"
                "9F81CC6",
                credential_ids=[
                    "credential_index_" + str(i)
                    for i in range(MAX_CREDENTIAL_ARRAY_LENGTH + 1)
                ],
            )

        self.assertEqual(
            err.exception.args[0],
            "{'credential_ids': 'CredentialIDs list cannot exceed "
            + str(MAX_CREDENTIAL_ARRAY_LENGTH)
            + " elements.'}",
        )

    def test_creds_list_duplicates(self):
        with self.assertRaises(XRPLModelException) as err:
            PaymentChannelClaim(
                account=_ACCOUNT,
                channel="5DB01B7FFED6B67E6B0414DED11E051D2EE2B7619CE0EAA6286D67A3A4D5B"
                "DB3",
                balance="1000",
                signature="304402204EF0AFB78AC23ED1C472E74F4299C0C21F1B21D07EFC0A3838A4"
                "20F76D783A400220154FB11B6F54320666E4C36CA7F686C16A3A0456800BBC43746F34"
                "AF50290064",
                public_key="023693F15967AE357D0327974AD46FE3C127113B1110D6044FD41E72368"
                "9F81CC6",
                credential_ids=["credential_index" for _ in range(5)],
            )

        self.assertEqual(
            err.exception.args[0],
            "{'credential_ids_duplicates': 'CredentialIDs list cannot contain duplicate"
            + " values.'}",
        )

    def test_creds_list_empty(self):
        with self.assertRaises(XRPLModelException) as err:
            PaymentChannelClaim(
                account=_ACCOUNT,
                channel="5DB01B7FFED6B67E6B0414DED11E051D2EE2B7619CE0EAA6286D67A3A4D5B"
                "DB3",
                balance="1000",
                signature="304402204EF0AFB78AC23ED1C472E74F4299C0C21F1B21D07EFC0A3838A"
                "420F76D783A400220154FB11B6F54320666E4C36CA7F686C16A3A0456800BBC43746F3"
                "4AF50290064",
                public_key="023693F15967AE357D0327974AD46FE3C127113B1110D6044FD41E72368"
                "9F81CC6",
                credential_ids=[],
            )
        self.assertEqual(
            err.exception.args[0],
            "{'credential_ids': 'CredentialIDs list cannot be empty.'}",
        )
