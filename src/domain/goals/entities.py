from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional

from core.domain import CreatedAtDomainMixin, EventDomainMixin
from domain.users.values import UserId
from domain.values import Title, Money
from .events import GoalAlreadyReachedEvent
from .exceptions import InvalidGoalDeadlineException
from .values import GoalId, GoalStatus


@dataclass(kw_only=True)
class Goal(CreatedAtDomainMixin, EventDomainMixin):
    """Доменная модель целей пользователей"""

    id: GoalId = field(default_factory=GoalId.generate)
    user_id: UserId
    title: Title
    target_amount: Money
    current_amount: Money = field(default=Money.zero)
    status: GoalStatus = field(default=GoalStatus.ACTIVE)
    deadline: Optional[datetime] = field(default=None)

    # TODO Подключить Minio S3
    # img_url: FileUrl

    @classmethod
    def create(
        cls,
        user_id: UserId,
        title: Title,
        target_amount: Money,
        current_amount: Money = Money(0),
        deadline: Optional[datetime] = None,
    ):
        if deadline and deadline.isoformat() < datetime.now().isoformat():
            raise InvalidGoalDeadlineException

        return cls(
            user_id=user_id,
            title=title,
            current_amount=current_amount,
            target_amount=target_amount,
            status=GoalStatus.ACTIVE,
            deadline=deadline,
        )

    def change_deadline(self, new_date: datetime) -> None:
        if new_date < datetime.now():
            raise InvalidGoalDeadlineException
        self.deadline = new_date

    def change_current_amount(self, new_current: Money) -> None:
        if new_current.as_generic_type() > self.target_amount.as_generic_type():
            self._events.append(
                GoalAlreadyReachedEvent(
                    goal_id=self.id.as_generic_type(),
                    user_id=self.user_id.as_generic_type(),
                )
            )
        self.current_amount = new_current

    @property
    def progress_percent(self) -> Decimal:
        return (
            self.current_amount.as_generic_type() / self.target_amount.as_generic_type()
        )
