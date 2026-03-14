import logging
from datetime import datetime, timedelta, timezone

from domain.accounts.exceptions import AccountNotFoundException
from domain.accounts.protocols import AccountRepositoryProtocol
from domain.accounts.values import AccountId
from domain.goals.exceptions import GoalNotFoundException
from domain.goals.protocols import GoalRepositoryProtocol
from domain.goals.values import GoalId
from domain.histories.protocols import HistoryRepositoryProtocol
from domain.users.values import UserId
from domain.values import Money, Percent
from .commands import ReserveCreateCommand
from .dto import FundDTO
from .entity import Fund, FundDistribution
from .exceptions import (
    FundNotFoundException,
    ReserveNotImplementedException,
    InvalidFundPercentageException,
)
from .protocol import FundRepositoryProtocol, FundDistRepositoryProtocol
from .values import FundReserveType, FundStatus
from ..histories.entities import History

logger = logging.getLogger(__name__)


class FundDistService:
    """Сервис работы с распределением остатка по процентам"""

    def __init__(
        self,
        fund_dist_repo: FundDistRepositoryProtocol,
        account_repo: AccountRepositoryProtocol,
        goal_repo: GoalRepositoryProtocol,
    ):
        self._fund_dist_repo = fund_dist_repo
        self._account_repo = account_repo
        self._goal_repo = goal_repo

    async def __check_reserve_id(
        self, reserve_id: str, user_id: str, reserve_type: FundReserveType
    ) -> None:
        """Получает необходимый резерв для остатка благодаря типу"""

        if reserve_type == FundReserveType.ACCOUNT:
            if not await self._account_repo.check_exists_by_id(user_id, reserve_id):
                # TODO Возможно добавить чуть подробные ошибки
                raise AccountNotFoundException

        elif reserve_type == FundReserveType.GOAL:
            if not await self._goal_repo.check_exists_by_id(user_id, reserve_id):
                raise GoalNotFoundException
        else:
            raise ReserveNotImplementedException

    async def _validate_input_reserves(
        self, user_id: str, reserves: list[ReserveCreateCommand]
    ) -> None:
        """Проверка всех входных резервов для распределения остатка"""
        total_percentage = 0

        for reserve in reserves:
            total_percentage += reserve.percent
            await self.__check_reserve_id(
                reserve_id=reserve.reserve_id,
                user_id=user_id,
                reserve_type=reserve.reserve_type,
            )

        if total_percentage != 100:
            logger.info(InvalidFundPercentageException.message)
            raise InvalidFundPercentageException

        logger.info("Резервы успешно провалидированы")


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
        self._fund_repo = fund_repo
        self._history_repo = history_repo

    async def create_or_update_fund(
        self, user_id: str, end_date: datetime, account_id: str
    ) -> str:
        """Создаем новый период или обновляем существующий"""

        open_fund = await self._fund_repo.get_last_opened(user_id)

        if open_fund:
            logger.info("Обновляем запись о накопленном остатке")
            return await self._update_fund(fund=open_fund, end_date=end_date)
        else:
            logger.info("Создаем новую запись о накопленном остатке")
            return await self._create_new_fund(
                account_id=account_id, user_id=user_id, end_date=end_date
            )

    async def _create_new_fund(
        self, account_id: str, user_id: str, end_date: datetime
    ) -> str:
        """
        Создаем новый период для остатка

        Если до этого закрытых периодов не было, то start_date становится значением даты создания первой записи
        Если до этого был закрытый период, то start_date = last_closed_date + 1
        """

        last_unopened_fund = await self._fund_repo.get_last_unopened(user_id=user_id)

        if last_unopened_fund:
            start_date = last_unopened_fund.end_date + timedelta(days=1)
            logger.info(start_date)

            if start_date > datetime.now(timezone.utc):
                logger.error("Накопленный остаток был сегодня уже распределен")
                return ""
        else:
            account = await self._account_repo.get_by_id(
                user_id=user_id, account_id=account_id
            )
            start_date = account.created_at

        total_amount = await self._history_repo.get_sum_delta_in_period(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
        )

        fund = Fund(
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

    async def get_unopened_funds(self, user_id: str) -> list[Fund]:
        """Получение распределенных остатков"""

        funds = await self._fund_repo.get_unopened(user_id)
        return funds

    async def close_head_fund(
        self, user_id: str, reserves: list[ReserveCreateCommand]
    ) -> None:
        """Закрытие последнего накопленного остатка"""

        await self._validate_input_reserves(user_id=user_id, reserves=reserves)

        last_open_fund = await self._fund_repo.get_last_opened(user_id)

        if not last_open_fund:
            logger.error(FundNotFoundException.message)
            raise FundNotFoundException

        all_fund_dists = []

        for reserve in reserves:
            amount = last_open_fund.total_amount.to_float() * (reserve.percent / 100)

            fund_dists = FundDistribution(
                fund_id=last_open_fund.id,
                reserve_id=(
                    AccountId(reserve.reserve_id)
                    if reserve.reserve_type == FundReserveType.ACCOUNT
                    else GoalId(reserve.reserve_id)
                ),
                reserve_type=reserve.reserve_type,
                percent_applied=Percent(reserve.percent),
                amount=Money(amount),
            )
            all_fund_dists.append(fund_dists)

        await self._fund_dist_repo.save_all(all_fund_dists, commit=False)

        last_open_fund.close()
        await self._fund_repo.update(
            user_id=user_id,
            fund_id=last_open_fund.id.as_generic_type(),
            upd_data=FundDTO.from_entity_to_dict(
                last_open_fund, excludes=["id", "user_id"]
            ),
            commit=False,
        )

        await self._distribute_user_fund(
            user_id=user_id, fund_id=last_open_fund.id.as_generic_type()
        )

    async def _distribute_user_fund(self, user_id: str, fund_id: str) -> None:
        fund_dists = await self._fund_dist_repo.get_by_find_id(fund_id)

        for fund_dist in fund_dists:

            if fund_dist.reserve_type == FundReserveType.ACCOUNT:
                account = await self._account_repo.get_by_id(
                    user_id=user_id, account_id=fund_dist.reserve_id.as_generic_type()
                )
                await self._account_repo.update(
                    user_id=user_id,
                    account_id=fund_dist.reserve_id.as_generic_type(),
                    upd_data={
                        "balance": (new_balance := fund_dist.amount.as_generic_type())
                    },
                    commit=False,
                )
                history = History(
                    account_id=account.id,
                    balance=Money(new_balance),
                    delta=float(new_balance),
                    is_monthly_closing=False,
                )
                await self._history_repo.save(history, commit=False)

            elif fund_dist.reserve_type == FundReserveType.GOAL:
                await self._goal_repo.update(
                    user_id=user_id,
                    goal_id=fund_dist.reserve_id.as_generic_type(),
                    upd_data={"current_amount": fund_dist.amount.as_generic_type()},
                    commit=False,
                )
            else:
                raise ReserveNotImplementedException

        fund = await self._fund_repo.get_by_id(fund_id)
        fund.status = FundStatus.DISTRIBUTED
        await self._fund_repo.update(
            user_id=user_id,
            fund_id=fund_id,
            upd_data={"status": FundStatus.DISTRIBUTED},
            commit=True,
        )
        return

    async def get_fund_by_id(self, user_id: str, fund_id: str) -> Fund:
        fund = await self._fund_repo.get_by_user_id(user_id, id=fund_id)
        if not fund:
            raise FundNotFoundException
        return fund
