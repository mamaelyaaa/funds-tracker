import logging
from datetime import datetime, timedelta

from domain.accounts.exceptions import AccountNotFoundException
from domain.accounts.protocols import AccountRepositoryProtocol
from domain.goals.exceptions import GoalNotFoundException
from domain.goals.protocols import GoalsRepositoryProtocol
from domain.histories.protocols import HistoryRepositoryProtocol
from domain.users.values import UserId
from domain.values import Money
from infra.repositories.funds import FundRepositoryDep
from infra.repositories.histories import HistoryRepositoryDep
from .commands import ReserveCreateCommand
from .entity import Fund
from .exceptions import (
    FundNotFoundException,
    ReserveNotImplementedException,
    InvalidFundPercentageException,
)
from .protocol import FundRepositoryProtocol
from .values import FundRuleType


class FundDistributionService:
    """Сервис работы с распределением остатка по процентам"""

    def __init__(
        self,
        account_repo: AccountRepositoryProtocol,
        goal_repo: GoalsRepositoryProtocol,
    ):
        self._account_repo = account_repo
        self._goal_repo = goal_repo

    async def __check_reserve_id(
        self, reserve_id: str, user_id: str, reserve_type: FundRuleType
    ) -> None:
        """Получает необходимый резерв для остатка благодаря типу"""

        if reserve_type == FundRuleType.ACCOUNT:
            if not await self._account_repo.check_exists_by_id(user_id, reserve_id):
                raise AccountNotFoundException

        elif reserve_type == FundRuleType.GOAL:
            if not await self._goal_repo.check_exists_by_id(user_id, reserve_id):
                raise GoalNotFoundException
        else:
            raise ReserveNotImplementedException

    async def _validate_input_reserves(
        self, reserves: list[ReserveCreateCommand]
    ) -> None:
        """Проверка всех входных резервов для распределения остатка"""
        total_percentage = 0

        for reserve in reserves:
            total_percentage += reserve.percent.as_generic_type()
            await self.__check_reserve_id(
                reserve_id=reserve.reserve_id,
                user_id=reserve.user_id,
                reserve_type=reserve.reserve_type,
            )

        if total_percentage != 100:
            raise InvalidFundPercentageException


logger = logging.getLogger(__name__)


class FundService(FundDistributionService):

    def __init__(
        self,
        fund_repo: FundRepositoryProtocol,
        history_repo: HistoryRepositoryProtocol,
        account_repo: AccountRepositoryProtocol,
        goal_repo: GoalsRepositoryProtocol,
    ):
        super().__init__(account_repo, goal_repo)
        self._fund_repo = fund_repo
        self._history_repo = history_repo

    async def create_or_update_fund(self, user_id: str, end_date: datetime) -> str:
        """Создаем новый период или обновляем существующий"""

        open_fund = await self._fund_repo.get_last_opened(user_id)

        if open_fund:
            logger.info("Обновляем запись о накопленном остатке")
            return await self._update_fund(fund=open_fund, end_date=end_date)
        else:
            logger.info("Создаем новую запись о накопленном остатке")
            return await self._create_new_fund(user_id=user_id, end_date=end_date)

    async def _create_new_fund(self, user_id: str, end_date: datetime) -> str:
        """
        Создаем новый период для остатка

        Если до этого закрытых периодов не было, то start_date становится значением даты создания первой записи
        Если до этого был закрытый период, то start_date = last_closed_date + 1
        """

        last_closed_fund = await self._fund_repo.get_last_closed(user_id)
        first_history_date = await self._history_repo.get_first_history_date_by_user(
            user_id
        )

        start_date = (
            last_closed_fund.end_date + timedelta(days=1)
            if last_closed_fund
            else first_history_date
        )

        total_amount = await self._history_repo.get_sum_delta_in_period(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
        )

        fund = Fund.create(
            user_id=UserId(user_id),
            total_amount=Money(total_amount),
            start_date=start_date,
            end_date=end_date,
        )
        fund_id = await self._fund_repo.save(fund)
        return fund_id

    async def _update_fund(self, fund: Fund, end_date: datetime) -> str:
        """Обновляет существующий остаток"""

        new_total = await self._history_repo.get_sum_delta_in_period(
            user_id=fund.user_id.as_generic_type(),
            end_date=end_date,
            start_date=fund.start_date,
        )

        data = {"total_amount": new_total, "end_date": end_date}

        await self._fund_repo.update(
            fund_id=fund.id.as_generic_type(),
            user_id=fund.user_id.as_generic_type(),
            upd_data=data,
        )
        return fund.id.as_generic_type()

    async def get_last_opened_fund(self, user_id: str) -> Fund:
        """Получение крайней нераспределенной записи об остатках"""

        fund = await self._fund_repo.get_last_opened(user_id)
        if not fund:
            raise FundNotFoundException
        return fund

    async def get_closed_funds(self, user_id: str) -> list[Fund]:
        funds = await self._fund_repo.get_closed(user_id)
        return funds

    async def close_head_fund(self, reserves: list[ReserveCreateCommand]):
        """Закрытие последнего накопленного остатка"""

        await self._validate_input_reserves(reserves)


def get_fund_service(
    fund_repo: FundRepositoryDep, history_repo: HistoryRepositoryDep
) -> FundService:
    return FundService(fund_repo=fund_repo, history_repo=history_repo)
