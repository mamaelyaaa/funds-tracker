import pytest
from faker.proxy import Faker

from domain.goals.entities import Goal
from domain.users.values import UserId
from domain.values import Money, Title


@pytest.mark.unit
@pytest.mark.goals
class TestGoalDomain:

    def test_create_success(self, test_goal):
        assert test_goal.current_amount == Money(0)
        assert test_goal.deadline is None

    def test_goal_already_reached(self, faker: Faker):
        goal = Goal.create(
            user_id=UserId("u-123"),
            title=Title(faker.word()),
            target_amount=Money(2000),
        )
        goal.change_current_amount(new_current=Money(2200))
        assert goal.current_amount == Money(2200)
        assert len(goal.events) == 1

    # def test_invalid_deadline(self, test_goal, faker: Faker):
    #     with pytest.raises(InvalidGoalDeadlineException):
    #         test_goal.change_deadline(
    #             new_date=faker.date_time(end_datetime=datetime.now(timezone.utc))
    #         )

    def test_progress_percentage(self, test_goal):
        assert (
            test_goal.progress_percent
            == test_goal.current_amount.as_generic_type()
            / test_goal.target_amount.as_generic_type()
        )
