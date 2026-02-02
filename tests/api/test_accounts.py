from typing import Callable

import pytest

from api.v1.schemas.accounts import AccountDetailSchema
from domain.accounts.values import AccountType, AccountCurrency
from domain.users.entity import User
from domain.users.values import UserId


@pytest.fixture
async def test_user(test_user_repository):
    user_id = UserId("u-123")
    user = User(id=user_id, name="user")
    await test_user_repository.save(user)

    saved_user = await test_user_repository.get_by_id(user.id)
    assert saved_user is not None
    assert saved_user.id.value == "u-123"

    yield user

    test_user_repository.clear()


@pytest.fixture
def account_data_factory() -> Callable:
    def factory(**overrides):
        defaults = {
            "name": "Накопительный",
            "initial_balance": 3000,
            "account_type": AccountType.CARD,
            "currency": AccountCurrency.RUB,
        }
        return {**defaults, **overrides}

    return factory


@pytest.mark.asyncio
class TestAccountCreateAPI:

    async def test_success(self, client, test_user, account_data_factory):
        data = account_data_factory(name="Основной счет")

        resp = await client.post(
            url=f"/api/v1/users/{test_user.id.value}/accounts",
            json=data,
        )
        assert resp.status_code == 201
        response_data = resp.json()

        account = AccountDetailSchema.model_validate(
            detail := response_data.get("detail")
        )

        assert account.balance == detail.get("balance")
        assert account.currency == detail.get("currency")
        assert account.type == detail.get("type")

    async def test_invalid_name_error(self, client, test_user, account_data_factory):
        data = account_data_factory(name="&!@#$")

        resp = await client.post(
            url=f"/api/v1/users/{test_user.id.value}/accounts",
            json=data,
        )
        assert resp.status_code == 400
        response_data = resp.json()
        assert "Попробуйте другое название" in response_data.get("suggestion")

    async def test_name_already_exists_conflict(
        self, client, test_user, account_data_factory
    ):
        data = account_data_factory(name="Дубликат")

        resp1 = await client.post(
            f"/api/v1/users/{test_user.id.value}/accounts", json=data
        )
        assert resp1.status_code == 201

        resp2 = await client.post(
            f"/api/v1/users/{test_user.id.value}/accounts", json=data
        )
        assert resp2.status_code == 409
        resp_data = resp2.json()
        assert "уже существует" in resp_data.get("message", "").lower()

    async def test_user_limit_accounts_conflict(
        self, client, test_user, test_account_repository, account_data_factory
    ):

        for i in range(test_user.MAX_ACCOUNTS):
            data = account_data_factory(name=f"Новый счет {i}")

            await client.post(
                url=f"/api/v1/users/{test_user.id.value}/accounts",
                json=data,
            )

        data = account_data_factory(
            name=f"Самый новый счет",
        )

        resp = await client.post(
            url=f"/api/v1/users/{test_user.id.value}/accounts",
            json=data,
        )

        assert resp.status_code == 409
        data = resp.json()
        assert "Превышен лимит" in data.get("message")


@pytest.mark.asyncio
class TestAccountGetAPI:

    ACCOUNTS_CREATE: int = 3

    @pytest.fixture(autouse=True)
    async def create_accounts(
        self, client, test_user, test_account_repository, account_data_factory
    ):
        test_account_repository.clear()
        self.accounts = []

        for i in range(self.ACCOUNTS_CREATE):
            data = account_data_factory(name=f"Счет {i}")

            resp = await client.post(
                url=f"/api/v1/users/{test_user.id.value}/accounts",
                json=data,
            )
            self.accounts.append(
                AccountDetailSchema.model_validate(resp.json()["detail"])
            )

        yield

    async def test_all_accounts_success(self, client, test_user):
        resp = await client.get(
            url=f"/api/v1/users/{test_user.id.value}/accounts",
        )

        assert resp.status_code == 200
        data: dict = resp.json()
        accounts = [
            AccountDetailSchema.model_validate(account) for account in data["detail"]
        ]

        assert data.get("message") == "Получение счётов пользователя"
        assert "metadata" in data

        assert len(accounts) == self.ACCOUNTS_CREATE
        assert accounts == self.accounts

    async def test_one_account_success(self, client, test_user):
        rand_account: AccountDetailSchema = self.accounts[0]

        resp = await client.get(
            url=f"/api/v1/users/{test_user.id.value}/accounts/{rand_account.id}",
        )
        assert resp.status_code == 200
        data: dict = resp.json()

        account = AccountDetailSchema.model_validate(data["detail"])

        assert account.id == rand_account.id
        assert account.type == rand_account.type
        assert account.balance == rand_account.balance
        assert account.currency == rand_account.currency

    async def test_one_account_not_found(self, client, test_user):
        resp = await client.get(
            url=f"/api/v1/users/{test_user.id.value}/accounts/unknown-account",
        )
        assert resp.status_code == 404
        response_data: dict = resp.json()

        assert "не найден" in response_data.get("message")
