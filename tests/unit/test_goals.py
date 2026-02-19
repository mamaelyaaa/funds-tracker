from datetime import datetime, timedelta

import pytest
from faker.proxy import Faker

from domain.accounts.values import AccountId
from domain.goals.entities import Goal
from domain.goals.exceptions import (
    InvalidGoalAmountsException,
    InvalidGoalDeadlineException,
)
from domain.goals.values import GoalStatus, GoalPercentage


@pytest.mark.unit
@pytest.mark.goals
class TestGoalDomain:

    def test_create_success(self, test_goal):
        assert test_goal.savings_percentage.as_generic_type() == 0.2
        assert test_goal.account_id is None
        assert test_goal.deadline is None
        assert test_goal.current_amount == 0

    def test_create_invalid_amount(self, faker: Faker):
        with pytest.raises(InvalidGoalAmountsException):
            Goal.create(
                user_id="u-123",
                title=faker.word(),
                target_amount=faker.pyfloat(positive=False),
            )

    def test_goal_already_reached(self, faker: Faker):
        goal = Goal.create(
            user_id="u-123",
            title=faker.word(),
            target_amount=2000,
        )
        goal.change_current_amount(new_current=2200)
        assert goal.current_amount == 2200
        assert len(goal._events) == 1

    def test_change_status(self, test_goal):
        test_goal.change_status(new_status=GoalStatus.FAILED)
        assert test_goal.status == GoalStatus.FAILED

    def test_change_percentage(self, test_goal):
        test_goal.change_percentage(new_percentage=GoalPercentage(0.3))
        assert test_goal.savings_percentage.as_generic_type() == 0.3

    def test_link_to_account(self, test_goal):
        test_goal.link_to_account(account_id=AccountId("acc-123"))
        assert test_goal.account_id._value == "acc-123"

    def test_change_deadline_success(self, test_goal):
        test_date = datetime.now() + timedelta(days=30)
        test_goal.change_deadline(new_date=test_date)
        assert test_goal.deadline == test_date

    def test_invalid_deadline(self, test_goal, faker: Faker):
        with pytest.raises(InvalidGoalDeadlineException):
            test_goal.change_deadline(
                new_date=faker.date_time(end_datetime=datetime.now())
            )

    def test_progress_percentage(self, test_goal):
        assert (
            test_goal.progress_percent
            == test_goal.current_amount / test_goal.target_amount
        )
