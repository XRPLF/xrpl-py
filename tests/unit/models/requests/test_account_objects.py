from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.requests import AccountObjects
from xrpl.models.requests.account_objects import AccountObjectType

_ACCOUNT = "rPT1Sjq2YGrBMTttX4GZHjKu9dyfzbpAYe"


class TestAccountObjectsTypeFilter(TestCase):
    def test_type_accepts_account_object_type_enum(self):
        req = AccountObjects(account=_ACCOUNT, type=AccountObjectType.ESCROW)
        self.assertTrue(req.is_valid())
        self.assertEqual(req.to_dict()["type"], "escrow")

    def test_type_accepts_lowercase_enum_value_string(self):
        req = AccountObjects(account=_ACCOUNT, type="escrow")
        self.assertTrue(req.is_valid())
        self.assertEqual(req.to_dict()["type"], "escrow")

    def test_type_accepts_canonical_ledger_entry_name(self):
        # rippled >= 2.4.0 supports canonical ledger entry names (e.g. "Escrow")
        # in the account_objects `type` filter. See XRPLF/xrpl-py#888.
        req = AccountObjects(account=_ACCOUNT, type="Escrow")
        self.assertTrue(req.is_valid())
        self.assertEqual(req.to_dict()["type"], "Escrow")

    def test_type_from_dict_accepts_canonical_ledger_entry_name(self):
        req = AccountObjects.from_dict({"account": _ACCOUNT, "type": "Escrow"})
        self.assertTrue(req.is_valid())
        self.assertEqual(req.to_dict()["type"], "Escrow")

    def test_type_still_rejects_non_string_values(self):
        with self.assertRaises(XRPLModelException):
            AccountObjects(account=_ACCOUNT, type=123)  # type: ignore[arg-type]
