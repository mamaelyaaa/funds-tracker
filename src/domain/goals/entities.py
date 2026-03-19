from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from core.mixins import DomainEventMixin, CreatedAtDomainMixin
from domain.users.values import UserId
from domain.values import Title, Money
from .events import GoalAlreadyReachedEvent
from .exceptions import InvalidGoalDeadlineException
from .values import GoalId, GoalStatus


@dataclass(kw_only=True)
class Goal(CreatedAtDomainMixin, DomainEventMixin):
    """Доменная модель целей пользователей"""

    id: GoalId = field(default_factory=GoalId)
    user_id: UserId
    title: Title
    target_amount: Money
    current_amount: Money = field(default=Money(0))
    status: GoalStatus = field(default=GoalStatus.ACTIVE)
    deadline: Optional[datetime] = field(default=None)

    # TODO Подключить Minio S3
    # img_url: FileUrl

    def __post_init__(self):
        if self.deadline and self.deadline.isoformat() < datetime.now().isoformat():
            raise InvalidGoalDeadlineException

    def change_deadline(self, new_date: datetime) -> None:
        if new_date < datetime.now(timezone.utc):
            raise InvalidGoalDeadlineException
        self.deadline = new_date

    def change_current_amount(self, new_current: Money) -> None:
        if new_current > self.target_amount:
            self._events.append(
                GoalAlreadyReachedEvent(
                    goal_id=self.id,
                    user_id=self.user_id,
                )
            )
        self.current_amount = new_current

    @property
    def progress_percent(self) -> Decimal:
        return self.current_amount / self.target_amount
