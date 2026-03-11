from domain.funds.events import FundClosedEvent
from infra.tasks.fund_distribution import distribute_user_fund_task
from .base import BaseTaskiqPublisher


class FundDistTaskiqPublisher(BaseTaskiqPublisher):

    def __init__(self):
        self.handlers = {
            FundClosedEvent: [self._handle_distribute_fund],
        }

    @staticmethod
    async def _handle_distribute_fund(event: FundClosedEvent) -> None:

        await distribute_user_fund_task.kiq(event)
        return
