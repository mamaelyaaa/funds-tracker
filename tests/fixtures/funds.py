from datetime import timezone, datetime

import pytest
from faker.proxy import Faker

from api.v1.dependencies.funds import get_fund_service
from domain.funds.entity import Fund
from domain.funds.service import FundService
from domain.values import Money


@pytest.fixture
def test_fund(test_user, faker: Faker) -> Fund:
    """Тестовый остаток"""

    return Fund(
        user_id=test_user.id,
        total_amount=Money(faker.pyfloat(positive=True)),
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + faker.time_delta(),
    )


@pytest.fixture
def test_fund_service(test_session) -> FundService:
    """Тестовый сервис остатков"""

    fund_service: FundService = get_fund_service(test_session)
    return fund_service
