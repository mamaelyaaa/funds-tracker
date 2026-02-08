# @pytest.mark.asyncio
# @pytest.mark.api
# class TestHistoryApi:
#
#     @pytest.fixture(autouse=True)
#     async def create_account_history(self, test_history_repo, faker: Faker) -> None:
#         self.history = []
#
#         def create_history(balance: float, created_at: datetime) -> History:
#             history = History(
#                 account_id=AccountId("acc-123"),
#                 balance=balance,
#                 created_at=created_at,
#             )
#             return history
#
#         for i in range(10):
#             rand_history = create_history(
#                 balance=faker.pyfloat(positive=True),
#                 created_at=datetime.combine(
#                     faker.date_between(
#                         start_date=datetime(year=2025, day=1, month=1),
#                         end_date=datetime(year=2026, day=1, month=2),
#                     ),
#                     time.min,
#                 ),
#             )
#             await test_history_repo.save(rand_history)
#             self.history.append(rand_history)
#
#         return
#
#     async def test_get_history_success(self, client, test_user, test_account):
#         response = await client.get(
#             url=f"/api/v1/users/{test_user.id.value}/accounts/{test_account.id.value}/history",
#             params={"interval": HistoryInterval.MONTH6.value},
#         )
#
#         assert response.status_code == 200
#         print(response.json())
#         print(self.history)
