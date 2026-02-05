from datetime import datetime

import pytest
from faker.proxy import Faker

from domain.accounts.exceptions import InvalidInitBalanceException
from domain.accounts.values import AccountId
from domain.histories.domain import History


@pytest.mark.unit
class TestHistoryDomain:

    def test_creation_success(self, faker: Faker):
        """Успешное создание истории"""

        balance = faker.pyfloat(positive=True)
        history = History.create(account_id=AccountId("acc-123"), balance=balance)

        assert history.created_at <= datetime.now()
        assert history.balance == balance

    def test_raise_invalid_balance(self, faker: Faker):
        """Проверка на невалидный баланс"""

        negative_balance = faker.pyfloat(positive=False)

        with pytest.raises(InvalidInitBalanceException):
            History.create(account_id=AccountId("acc-321"), balance=negative_balance)
