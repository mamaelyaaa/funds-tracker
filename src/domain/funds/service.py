import asyncio
import logging
from datetime import datetime, timedelta, timezone

from api.schemas import PaginationMetaSchema
from domain.accounts.exceptions import AccountNotFoundException
from domain.accounts.protocols import AccountRepositoryProtocol
from domain.goals.exceptions import GoalNotFoundException
from domain.goals.protocols import GoalRepositoryProtocol
from domain.histories.protocols import HistoryRepositoryProtocol
from domain.users.values import UserId
from domain.values import Money
from infra.database.specification import PaginationSpecification
from .commands import (
    CreateOrUpdateFundCommand,
    CheckReserveCommand,
    CreateReservesCommand,
    GetFundsCommand,
    GetFundCommand,
)
from .entity import Fund
from .exceptions import (
    FundNotFoundException,
    ReserveNotImplementedException,
    InvalidFundPercentageException,
    FundAlreadyDistributedTodayException,
)
from .protocol import FundRepositoryProtocol, FundDistRepositoryProtocol
from .values import FundReserveType

logger = logging.getLogger("fund.service")


class FundDistService:
    """Сервис работы с распределением остатка по процентам"""

    def __init__(
        self,
        fund_dist_repo: FundDistRepositoryProtocol,
        account_repo: AccountRepositoryProtocol,
        goal_repo: GoalRepositoryProtocol,
    ):
        self.fund_dist_repo = fund_dist_repo
        self.account_repo = account_repo
        self.goal_repo = goal_repo

    async def _check_reserve_id(self, command: CheckReserveCommand) -> None:
        """Получает необходимый резерв для остатка благодаря типу"""

        if command.reserve_type == FundReserveType.ACCOUNT:
            if not await self.account_repo.check_exists_by_id(
                command.user_id, command.reserve_id
            ):
                raise AccountNotFoundException

        elif command.reserve_type == FundReserveType.GOAL:
            if not await self.goal_repo.check_exists_by_id(
                command.user_id, command.reserve_id
            ):
                raise GoalNotFoundException
        else:
            raise ReserveNotImplementedException

    async def validate_input_reserves(self, command: CreateReservesCommand) -> None:
        """Проверка всех входных резервов для распределения остатка"""

        total_percentage = 0

        for reserve in command.reserves:
            total_percentage += reserve.percent

            await self._check_reserve_id(
                command=CheckReserveCommand(
                    reserve_id=reserve.reserve_id,
                    user_id=command.user_id,
                    reserve_type=reserve.reserve_type,
                )
            )

        if total_percentage != 100:
            logger.warning("Неправильное распределение по процентам")
            raise InvalidFundPercentageException

        logger.info("Резервы успешно провалидированы")
        return


class FundService(FundDistService):

    def __init__(
        self,
        fund_repo: FundRepositoryProtocol,
        history_repo: HistoryRepositoryProtocol,
        fund_dist_repo: FundDistRepositoryProtocol,
        account_repo: AccountRepositoryProtocol,
        goal_repo: GoalRepositoryProtocol,
    ):
        super().__init__(
            fund_dist_repo=fund_dist_repo,
            account_repo=account_repo,
            goal_repo=goal_repo,
        )
        self.fund_repo = fund_repo
        self.history_repo = history_repo

    async def create_or_update_fund(self, command: CreateOrUpdateFundCommand) -> str:
        """Создаем новый период или обновляем существующий"""

        # Получаем крайний открытый накопительный остаток
        open_fund = await self.fund_repo.get_last_opened(command.user_id)

        if open_fund:
            logger.info("Обновляем запись о накопленном остатке")
            return await self._update_fund(fund=open_fund, end_date=command.end_date)
        else:
            logger.info("Создаем новую запись о накопленном остатке")
            return await self._create_new_fund(command)

    async def _create_new_fund(self, command: CreateOrUpdateFundCommand) -> str:
        """
        Создаем новый период для остатка

        Если до этого закрытых периодов не было, то start_date становится значением даты создания первой записи
        Если до этого был закрытый период, то start_date = last_closed_date + 1
        """

        last_unopened_fund = await self.fund_repo.get_last_unopened(
            user_id=command.user_id
        )

        if last_unopened_fund:
            start_date = last_unopened_fund.end_date + timedelta(days=1)
            logger.info(start_date)

            if start_date > datetime.now(timezone.utc):
                logger.error("Накопленный остаток был сегодня уже распределен")
                return ""
        else:
            account = await self.account_repo.find_one(
                user_id=command.user_id, id=command.account_id
            )
            start_date = account.created_at

        total_amount = await self.history_repo.get_sum_delta_in_period(
            user_id=command.user_id,
            start_date=start_date,
            end_date=command.end_date,
        )

        fund = Fund(
            user_id=UserId(command.user_id),
            total_amount=Money(total_amount),
            start_date=start_date,
            end_date=command.end_date,
        )
        fund_id = await self.fund_repo.save(fund)
        return fund_id

    async def _update_fund(self, fund: Fund, end_date: datetime) -> str:
        """Обновляет существующий остаток"""

        new_total = await self.history_repo.get_sum_delta_in_period(
            user_id=fund.user_id.as_generic_type(),
            end_date=end_date,
            start_date=fund.start_date,
        )

        data = {"total_amount": new_total, "end_date": end_date}

        await self.fund_repo.update(
            fund_id=fund.id.as_generic_type(),
            user_id=fund.user_id.as_generic_type(),
            upd_data=data,
        )
        return fund.id.as_generic_type()

    async def get_last_opened_fund(self, user_id: str) -> Fund:
        """Получение крайней нераспределенной записи об остатках"""

        last_closed = await self.fund_repo.get_last_unopened(user_id)
        if last_closed and last_closed.end_date.day == datetime.now(timezone.utc).day:
            raise FundAlreadyDistributedTodayException

        fund = await self.fund_repo.get_last_opened(user_id)
        if not fund:
            raise FundNotFoundException
        return fund

    async def get_unopened_funds(
        self, command: GetFundsCommand
    ) -> tuple[list[Fund], PaginationMetaSchema]:
        """Получение распределенных остатков"""

        funds, funds_count = await asyncio.gather(
            self.fund_repo.get_unopened(
                command.user_id,
                PaginationSpecification.from_pagination_command(command.pagination),
            ),
            self.fund_repo.get_count_by_user_id(command.user_id),
        )

        return funds, PaginationMetaSchema(
            page=command.pagination.page,
            limit=command.pagination.limit,
            total_found=funds_count,
        )

    async def get_fund_by_id(self, command: GetFundCommand) -> Fund:
        """Получение остатка по уникальному id"""

        fund = await self.fund_repo.find_one(
            id=command.fund_id,
            user_id=command.user_id,
        )
        if not fund:
            raise FundNotFoundException
        return fund
