"""Fee calculation for the transactions rippled charges an owner reserve."""

from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch

from xrpl.asyncio.transaction.main import _calculate_fee_per_transaction_type
from xrpl.models.currencies import XRP
from xrpl.models.transactions import AccountDelete, AMMCreate, Transaction, VaultCreate

_MODULE = "xrpl.asyncio.transaction.main"
_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_DESTINATION = "ra5nK24KXen9AHvsdFTKHSANinZseWnPcX"
_BASE_FEE = "10"
_OWNER_RESERVE_FEE = 200000


class TestOwnerReserveFee(IsolatedAsyncioTestCase):
    async def _fee(self, transaction: Transaction) -> str:
        with (
            patch(f"{_MODULE}.get_fee", new=AsyncMock(return_value=_BASE_FEE)),
            patch(
                f"{_MODULE}._fetch_owner_reserve_fee",
                new=AsyncMock(return_value=_OWNER_RESERVE_FEE),
            ),
        ):
            return await _calculate_fee_per_transaction_type(transaction, client=None)

    async def test_account_delete_pays_owner_reserve(self):
        tx = AccountDelete(account=_ACCOUNT, destination=_DESTINATION)
        self.assertEqual(await self._fee(tx), str(_OWNER_RESERVE_FEE))

    async def test_amm_create_pays_owner_reserve(self):
        tx = AMMCreate(account=_ACCOUNT, amount="100", amount2="200", trading_fee=12)
        self.assertEqual(await self._fee(tx), str(_OWNER_RESERVE_FEE))

    async def test_vault_create_pays_base_fee(self):
        # rippled 3.2.0 stopped charging VaultCreate an owner reserve
        # (XRPLF/rippled#5954), so it pays the reference fee like any transaction.
        tx = VaultCreate(account=_ACCOUNT, asset=XRP())
        self.assertEqual(await self._fee(tx), _BASE_FEE)
