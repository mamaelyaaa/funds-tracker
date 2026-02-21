from datetime import datetime

import pytest
from faker.proxy import Faker

from domain.accounts.exceptions import InvalidBalanceException
from domain.histories.entities import History


@pytest.mark.unit
class TestHistoryDomain:

    def test_creation_success(self, faker: Faker):
        """Успешное создание истории"""

        balance = faker.pyfloat(positive=True)
        history = History.create(account_id="acc-123", balance=balance, delta=0)

        assert history.created_at <= datetime.now()
        assert history.balance == balance

    def test_raise_invalid_balance(self, faker: Faker):
        """Проверка на невалидный баланс"""

        with pytest.raises(InvalidBalanceException):
            History.create(
                account_id="acc-321", balance=faker.pyfloat(positive=False), delta=0
            )
