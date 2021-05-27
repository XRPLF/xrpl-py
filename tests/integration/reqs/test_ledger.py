import inspect
from unittest import IsolatedAsyncioTestCase

from tests.integration.it_utils import ASYNC_JSON_RPC_CLIENT, JSON_RPC_CLIENT
from xrpl.models.requests import Ledger


def test_async_and_sync(test_function):
    sync_code = inspect.getsource(test_function)
    sync_code = (
        sync_code.replace("async def", "def")  # convert method from async to sync
        .replace("await ", "")  # replace function calls
        .replace("@test_async_and_sync\n    ", "")  # avoid decorator recursion
        # .replace("_async", "") # change methods
        .replace("\n    ", "\n")  # remove indenting (syntax error otherwise)
        .replace("    def", "def")  # remove more indenting
    )
    first_line = inspect.getsourcelines(test_function)[0][1]
    sync_code += first_line.replace("    async def ", "").replace(":", "")
    print(sync_code)

    async def modified_test(self):
        with self.subTest(version="sync"):
            exec(sync_code, globals(), {"self": self, "client": JSON_RPC_CLIENT})
            # NOTE: passing `globals()` into `exec` is really bad practice and not safe
            # at all, but in this case it's fine because it's only running test code
            print("success")
        with self.subTest(version="async"):
            await test_function(self, ASYNC_JSON_RPC_CLIENT)

    return modified_test


class TestLedger(IsolatedAsyncioTestCase):
    @test_async_and_sync
    async def test_basic_functionality(self, client):
        response = await client.request(Ledger())
        print(response)
        self.assertTrue(response.is_successful())
