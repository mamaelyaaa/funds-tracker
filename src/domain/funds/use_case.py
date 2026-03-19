from domain.accounts.commands import UpdateAccountBalanceCommand
from domain.accounts.service import AccountService
from domain.accounts.values import AccountId
from domain.funds.commands import (
    CreateReserveCommand,
    CreateReservesCommand,
)
from domain.funds.dto import FundDTO
from domain.funds.entity import FundDistribution, Fund
from domain.funds.exceptions import ReserveNotImplementedException
from domain.funds.service import FundService
from domain.funds.values import FundReserveType, FundStatus
from domain.goals.command import UpdateGoalPartiallyCommand
from domain.goals.service import GoalService
from domain.goals.values import GoalId
from domain.values import Money, Percentage


class FundDistUseCase:

    def __init__(
        self,
        fund_service: FundService,
        account_service: AccountService,
        goal_service: GoalService,
    ):
        self.fund_service = fund_service
        self.account_service = account_service
        self.goal_service = goal_service

    async def close_head_fund(self, command: CreateReservesCommand):
        """Закрытие и распределение остатка"""

        await self.fund_service.validate_input_reserves(
            command=CreateReservesCommand(
                user_id=command.user_id, reserves=command.reserves
            )
        )

        last_open_fund = await self.fund_service.get_last_opened_fund(command.user_id)
        await self._create_fund_distributions(last_open_fund, command.reserves)

        last_open_fund.close()
        await self.fund_service.fund_repo.update(
            user_id=command.user_id,
            fund_id=last_open_fund.id,
            upd_data=FundDTO.from_entity_to_dict(
                last_open_fund, excludes=["id", "user_id"]
            ),
            commit=False,
        )

        await self._distribute_user_fund(
            user_id=command.user_id, fund_id=last_open_fund.id
        )

    async def _create_fund_distributions(
        self, last_open_fund: Fund, reserves: list[CreateReserveCommand]
    ) -> None:
        all_fund_dists = []

        for reserve in reserves:
            amount = last_open_fund.total_amount * (reserve.percent / 100)

            fund_dists = FundDistribution(
                fund_id=last_open_fund.id,
                reserve_id=(
                    AccountId(reserve.reserve_id)
                    if reserve.reserve_type == FundReserveType.ACCOUNT
                    else GoalId(reserve.reserve_id)
                ),
                reserve_type=reserve.reserve_type,
                percent_applied=Percentage.from_percent(reserve.percent),
                amount=Money(amount),
            )
            all_fund_dists.append(fund_dists)

        await self.fund_service.fund_dist_repo.save_all(all_fund_dists, commit=False)

    async def _distribute_user_fund(self, user_id: str, fund_id: str) -> None:
        fund_dists = await self.fund_service.fund_dist_repo.find_all(fund_id=fund_id)

        for fund_dist in fund_dists:

            if fund_dist.reserve_type == FundReserveType.ACCOUNT:
                account = await self.account_service.repository.find_one(
                    user_id=user_id, id=fund_dist.reserve_id
                )
                new_balance = account.balance + fund_dist.amount
                await self.account_service.update_balance(
                    command=UpdateAccountBalanceCommand(
                        user_id=user_id,
                        account_id=fund_dist.reserve_id,
                        new_balance=new_balance,
                        is_monthly_closing=False,
                    )
                )

            elif fund_dist.reserve_type == FundReserveType.GOAL:
                goal = await self.goal_service.goal_repo.find_one(
                    user_id=user_id, id=fund_dist.reserve_id
                )
                new_balance = goal.current_amount + fund_dist.amount
                await self.goal_service.update_goal_partially(
                    command=UpdateGoalPartiallyCommand(
                        user_id=user_id,
                        goal_id=fund_dist.reserve_id,
                        current_amount=new_balance,
                    )
                )
            else:
                raise ReserveNotImplementedException

        fund = await self.fund_service.fund_repo.find_one(id=fund_id)
        fund.status = FundStatus.DISTRIBUTED

        await self.fund_service.fund_repo.update(
            user_id=user_id,
            fund_id=fund_id,
            upd_data={"status": FundStatus.DISTRIBUTED},
            commit=True,
        )
        return
