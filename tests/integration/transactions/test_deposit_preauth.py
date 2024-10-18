from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import WALLET
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import DepositPreauth
from xrpl.models.transactions.deposit_preauth import Credential
from xrpl.utils import str_to_hex

ACCOUNT = WALLET.address
ADDRESS = "rEhxGqkqPPSxQ3P25J66ft5TwpzV14k2de"


class TestDepositPreauth(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_authorize(self, client):
        deposit_preauth = DepositPreauth(
            account=ACCOUNT,
            authorize=ADDRESS,
        )
        response = await sign_and_reliable_submission_async(
            deposit_preauth, WALLET, client
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)

    @test_async_and_sync(globals())
    async def test_unauthorize(self, client):
        deposit_preauth = DepositPreauth(
            account=ACCOUNT,
            unauthorize=ADDRESS,
        )
        response = await sign_and_reliable_submission_async(
            deposit_preauth, WALLET, client
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)

    @test_async_and_sync(globals())
    async def test_credentials_array_input_fields(self, client):
        sample_credentials = [
            Credential(issuer=ADDRESS, credential_type=str_to_hex("SampleCredType"))
        ]

        # Test the authorize_credentials input field
        deposit_preauth = DepositPreauth(
            account=ACCOUNT,
            authorize_credentials=sample_credentials,
        )
        response = await sign_and_reliable_submission_async(
            deposit_preauth, WALLET, client
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)

        # Test the unauthorize_credentials input field
        deposit_preauth = DepositPreauth(
            account=ACCOUNT,
            unauthorize_credentials=sample_credentials,
        )
        response = await sign_and_reliable_submission_async(
            deposit_preauth, WALLET, client
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
