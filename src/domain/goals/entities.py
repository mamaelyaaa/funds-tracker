from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any

from core.domain import DomainEntity
from domain.accounts.values import AccountId, Title
from .events import GoalAlreadyReachedEvent, GoalLinkedToAccountEvent
from .exceptions import InvalidGoalDeadlineException, InvalidGoalAmountsException
from .values import GoalId, GoalStatus, GoalPercentage
from ..users.values import UserId


@dataclass(kw_only=True)
class Goal(DomainEntity):
    """Доменная модель целей пользователей"""

    id: GoalId = field(default_factory=GoalId.generate)
    user_id: UserId
    account_id: Optional[AccountId] = field(default=None)

    title: Title
    target_amount: float
    current_amount: float = field(default=0)

    status: GoalStatus = field(default=GoalStatus.ACTIVE)
    deadline: Optional[datetime] = field(default=None)

    savings_percentage: Optional[GoalPercentage]

    # TODO Подключить Minio S3
    # img_url: FileUrl

    @classmethod
    def create(
        cls,
        user_id: str,
        title: str,
        target_amount: float,
        savings_percentage: float = 0.2,
        account_id: Optional[str] = None,
        deadline: Optional[datetime] = None,
    ):
        if target_amount < 0:
            raise InvalidGoalAmountsException

        return cls(
            user_id=UserId(user_id),
            title=Title(title),
            account_id=account_id,
            target_amount=target_amount,
            status=GoalStatus.ACTIVE,
            deadline=deadline,
            savings_percentage=GoalPercentage(savings_percentage),
        )

    def change_deadline(self, new_date: datetime) -> None:
        if new_date < datetime.now():
            raise InvalidGoalDeadlineException
        self.deadline = new_date

    def change_current_amount(self, new_current: float) -> None:
        if new_current < 0:
            raise InvalidGoalAmountsException
        if new_current > self.target_amount:
            self._events.append(
                GoalAlreadyReachedEvent(
                    goal_id=self.id,
                    account_id=self.account_id,
                )
            )
        self.current_amount = new_current

    def change_target_amount(self, new_target: float) -> None:
        if new_target < 0:
            raise InvalidGoalAmountsException
        self.target_amount = new_target

    def change_status(self, new_status: GoalStatus) -> None:
        self.status = new_status

    def link_to_account(self, account_id: AccountId) -> None:
        if self.account_id:
            self._events.append(
                GoalLinkedToAccountEvent(
                    account_id=self.account_id.as_generic_type(),
                    goal_id=self.id.as_generic_type(),
                    user_id=self.user_id.as_generic_type(),
                )
            )
        self.account_id = account_id

    def unlink_account(self) -> None:
        self.account_id = None

    def change_percentage(self, new_percentage: GoalPercentage) -> None:
        self.savings_percentage = new_percentage

    def change_title(self, new_title: str) -> None:
        self.title = Title(new_title)

    @property
    def progress_percent(self) -> float:
        return self.current_amount / self.target_amount

    def to_dict(self, all_str: bool = False) -> dict[str, Any]:
        return {
            "id": self.id.as_generic_type(),
            "user_id": self.user_id.as_generic_type(),
            "account_id": (
                self.account_id.as_generic_type() if self.account_id else None
            ),
            "title": self.title.as_generic_type(),
            "target_amount": self.target_amount,
            "savings_percentage": (
                self.savings_percentage.as_generic_type()
                if self.savings_percentage
                else None
            ),
            "deadline": self.deadline if self.deadline else None,
        }
