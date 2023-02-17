from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import Hook, SetHook

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_FEE = "0.00001"
_SEQUENCE = 19048
_BINARY = "0061736D01000000011C0460057F7F7F7F7F017E"
"60037F7F7E017E60027F7F017F60017F017E02230303656E76057"
"472616365000003656E7606616363657074000103656E76025F67"
"0002030201030503010002062B077F0141B088040B7F004180080"
"B7F0041A6080B7F004180080B7F0041B088040B7F0041000B7F00"
"41010B07080104686F6F6B00030AC4800001C0800001017F23004"
"1106B220124002001200036020C41920841134180084112410010"
"001A410022002000420010011A41012200200010021A200141106"
"A240042000B0B2C01004180080B254163636570742E633A204361"
"6C6C65642E00224163636570742E633A2043616C6C65642E22"
_HOOK_ON = "000000000000000000000000000000000000000000"
"000000000000003E3FF5B7"
_NAMESPACE = "4FF9961269BF7630D32E15276569C94470174A5D"
"A79FA567C0F62251AA9A36B9"
_VERSION = 0
_FLAGS = 1


class TestSetHook(TestCase):
    def test_invalid_hook_on(self):
        with self.assertRaises(XRPLModelException):
            hook = Hook(
                create_code=_BINARY,
                flags=_FLAGS,
                hook_api_version=_VERSION,
                hook_namespace=_NAMESPACE,
                hook_on="",
            )
            SetHook(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                hooks=[hook],
            )

    def test_invalid_hook_namespace(self):
        with self.assertRaises(XRPLModelException):
            hook = Hook(
                create_code=_BINARY,
                flags=_FLAGS,
                hook_api_version=_VERSION,
                hook_namespace="",
                hook_on=_HOOK_ON,
            )
            SetHook(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                hooks=[hook],
            )

    def test_invalid_num_hooks(self):
        with self.assertRaises(XRPLModelException):
            hook = Hook(
                create_code=_BINARY,
                flags=_FLAGS,
                hook_api_version=_VERSION,
                hook_namespace=_NAMESPACE,
                hook_on=_HOOK_ON,
            )
            SetHook(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                hooks=[
                    hook,
                    hook,
                    hook,
                    hook,
                    hook,
                ],
            )
