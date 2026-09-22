from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import WALLET
from xrpl.models import CheckCreate, SponsorshipSet
from xrpl.models.requests import AccountObjects, AccountObjectType
from xrpl.wallet import Wallet

# Sponsor-type flag: draw the created object's reserve from the sponsorship.
_TF_SPONSOR_RESERVE = 0x00000002


class TestAccountObjects(IntegrationTestCase):
    """Coverage for the XLS-68 additions to `account_objects`:

    * the `sponsored` boolean filter, which partitions an account's owned
      objects into sponsored (reserve paid by a sponsor) and self-funded; and
    * `type=SPONSORSHIP`, which returns the `Sponsorship` budget object.

    Each `SponsorshipSet` passes a `fee_amount_delta`: a create must leave the
    object with a positive budget, or rippled rejects it with `tecNO_PERMISSION`.
    """

    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        response = await client.request(
            AccountObjects(
                account=WALLET.address,
            )
        )
        self.assertTrue(response.is_successful())

    @test_async_and_sync(globals())
    async def test_sponsored_filter_partitions_owned_objects(self, client):
        """The `sponsored` filter splits an account's owned objects.

        The sponsee owns two Checks: one whose reserve is sponsored (so the
        object carries a `Sponsor` field) and one it funds itself.
        `sponsored=True` must return only the former, `sponsored=False` only
        the latter, and omitting the field returns both.
        """
        sponsor_wallet = Wallet.create()
        sponsee_wallet = Wallet.create()
        destination_wallet = Wallet.create()
        await fund_wallet_async(sponsor_wallet)
        await fund_wallet_async(sponsee_wallet)
        await fund_wallet_async(destination_wallet)

        # Sponsor pre-funds a reserve budget so the sponsee can create a
        # sponsored object on its own, with no co-signature.
        create_resp = await sign_and_reliable_submission_async(
            SponsorshipSet(
                account=sponsor_wallet.address,
                sponsee=sponsee_wallet.address,
                fee_amount_delta="1000000",
                remaining_owner_count_delta=2,
            ),
            sponsor_wallet,
            client,
        )
        self.assertEqual(create_resp.result["engine_result"], "tesSUCCESS")

        # A sponsored Check: its reserve is drawn from the sponsorship, so the
        # object carries a `Sponsor` field.
        sponsored_check = await sign_and_reliable_submission_async(
            CheckCreate(
                account=sponsee_wallet.address,
                destination=destination_wallet.address,
                send_max="1000000",
                sponsor=sponsor_wallet.address,
                sponsor_flags=_TF_SPONSOR_RESERVE,
            ),
            sponsee_wallet,
            client,
        )
        self.assertEqual(sponsored_check.result["engine_result"], "tesSUCCESS")

        # A plain Check the sponsee funds itself.
        plain_check = await sign_and_reliable_submission_async(
            CheckCreate(
                account=sponsee_wallet.address,
                destination=destination_wallet.address,
                send_max="1000000",
            ),
            sponsee_wallet,
            client,
        )
        self.assertEqual(plain_check.result["engine_result"], "tesSUCCESS")

        # sponsored=True -> only the sponsored object.
        only_sponsored = await client.request(
            AccountObjects(account=sponsee_wallet.address, sponsored=True)
        )
        self.assertTrue(only_sponsored.is_successful())
        sponsored_objs = only_sponsored.result["account_objects"]
        self.assertGreater(len(sponsored_objs), 0)
        self.assertTrue(all("Sponsor" in obj for obj in sponsored_objs))

        # sponsored=False -> the self-funded object, plus the Sponsorship
        # object itself (it links both accounts, so it sits in the sponsee's
        # directory too, and is not itself sponsored).
        only_plain = await client.request(
            AccountObjects(account=sponsee_wallet.address, sponsored=False)
        )
        self.assertTrue(only_plain.is_successful())
        plain_objs = only_plain.result["account_objects"]
        self.assertGreater(len(plain_objs), 0)
        self.assertTrue(all("Sponsor" not in obj for obj in plain_objs))

        # The two filters partition the account's objects: every object is
        # either sponsored or not, so their counts must sum to the unfiltered
        # total. (This holds regardless of the Sponsorship object above.)
        all_resp = await client.request(AccountObjects(account=sponsee_wallet.address))
        self.assertTrue(all_resp.is_successful())
        self.assertEqual(
            len(all_resp.result["account_objects"]),
            len(sponsored_objs) + len(plain_objs),
        )

    @test_async_and_sync(globals())
    async def test_type_sponsorship_filter(self, client):
        """`type=SPONSORSHIP` returns the Sponsorship object on the sponsor."""
        sponsor_wallet = Wallet.create()
        sponsee_wallet = Wallet.create()
        await fund_wallet_async(sponsor_wallet)
        await fund_wallet_async(sponsee_wallet)

        create_resp = await sign_and_reliable_submission_async(
            SponsorshipSet(
                account=sponsor_wallet.address,
                sponsee=sponsee_wallet.address,
                fee_amount_delta="1000000",
            ),
            sponsor_wallet,
            client,
        )
        self.assertEqual(create_resp.result["engine_result"], "tesSUCCESS")

        # The Sponsorship object lives in the sponsor's directory.
        account_objects_response = await client.request(
            AccountObjects(
                account=sponsor_wallet.address,
                type=AccountObjectType.SPONSORSHIP,
            )
        )
        self.assertTrue(account_objects_response.is_successful())
        sponsorship_objects = account_objects_response.result["account_objects"]
        self.assertGreater(len(sponsorship_objects), 0)
        for obj in sponsorship_objects:
            self.assertEqual(obj["LedgerEntryType"], "Sponsorship")
