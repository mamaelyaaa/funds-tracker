from datetime import timezone, datetime

import pytest
from asyncpg.pgproto.pgproto import timedelta
from faker.proxy import Faker

from domain.funds.entity import Fund
from domain.funds.exceptions import InvalidFundDateException
from domain.funds.values import FundStatus
from domain.users.values import UserId
from domain.values import Money


@pytest.mark.unit
@pytest.mark.funds
class TestFundDomain:

    def test_create_fund(self, faker: Faker):
        """Успешное создание остатка"""

        fund = Fund(
            user_id=UserId("u-123"),
            total_amount=Money(faker.pyfloat(positive=True)),
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(minutes=30),
        )

        assert fund.status == FundStatus.OPEN
        assert fund.total_amount.value() >= 0
        assert fund.start_date <= fund.end_date

    def test_invalid_data(self, faker: Faker):
        """Создание с ошибкой в датах"""

        with pytest.raises(InvalidFundDateException):
            Fund(
                user_id=UserId("u-123"),
                total_amount=Money(faker.pyfloat(positive=True)),
                start_date=datetime.now(timezone.utc),
                end_date=datetime.now(timezone.utc) - timedelta(days=1),
            )
