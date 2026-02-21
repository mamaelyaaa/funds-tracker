# @pytest.fixture
# def test_history(test_account) -> History:
#     return History.create(
#         account_id=test_account.id.as_generic_type(), balance=test_account.balance
#     )
#
#
# @pytest.fixture
# def test_history_repo() -> HistoryRepositoryProtocol:
#     return InMemoryHistoryRepository()
#
#
# @pytest.fixture
# def test_goal_publisher() -> GoalsEventPublisherProtocol:
#     return GoalsTaskiqPublisher()
#
#
# @pytest.fixture
# def test_history_service(test_goal_repo) -> GoalsService:
#     return GoalsService(goals_repo=test_goal_repo)
