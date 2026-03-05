from datetime import datetime

import pytest
from black import timezone
from faker.proxy import Faker

from domain.accounts.values import AccountId
from domain.histories.entities import History
from domain.values import Money


@pytest.mark.unit
@pytest.mark.history
class TestHistoryDomain:

    def test_creation_success(self, faker: Faker):
        """Успешное создание истории"""

        balance = Money(faker.pyfloat(positive=True))
        history = History(
            account_id=AccountId("acc-123"),
            balance=balance,
            is_monthly_closing=False,
        )

        assert history.created_at <= datetime.now(timezone.utc)
        assert history.balance == balance
