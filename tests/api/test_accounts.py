import pytest
from faker.proxy import Faker

from domain.accounts.entity import Account
from domain.accounts.values import AccountCurrency, AccountType


@pytest.mark.asyncio
@pytest.mark.accounts
@pytest.mark.api
class TestAccountApi:

    async def test_create_success(self, client, saved_user):
        response = await client.post(
            url=f"/api/v1/users/{saved_user.id.value}/accounts",
            json={
                "name": "Новый счет",
                "initial_balance": 1000,
                "currency": "RUB",
                "account_type": "Card",
            },
        )
        assert response.status_code == 201
        assert response.headers["content-type"] == "application/json"
        assert "message" in response.json()
        detail: dict = response.json()["detail"]

        assert detail["name"] == "Новый счет"
        assert detail["balance"] == 1000
        assert detail["currency"] == "RUB"
        assert detail["type"] == "Card"
        assert "createdAt" in detail
        assert "id" in detail

    @pytest.mark.parametrize("account_name", [("%^%&$^#(%", "  ", "")])
    async def test_invalid_account_name(self, client, saved_user, account_name):
        response = await client.post(
            url=f"/api/v1/users/{saved_user.id.value}/accounts",
            json={
                "name": account_name,
                "initial_balance": 1000,
                "currency": "RUB",
                "account_type": "Card",
            },
        )
        assert response.status_code in (400, 422)

    async def test_account_already_exists(self, client, saved_user, test_account_repo):
        account = Account.create(
            user_id=saved_user.id.value,
            name="Новый счет",
            balance=2000,
            currency=AccountCurrency.RUB,
            account_type=AccountType.CARD,
        )
        await test_account_repo.save(account)

        response = await client.post(
            url=f"/api/v1/users/{saved_user.id.value}/accounts",
            json={
                "name": "Новый счет",
                "initial_balance": 1000,
                "currency": "RUB",
                "account_type": "Card",
            },
        )
        assert response.status_code == 409
        response_data = response.json()
        assert "message" in response_data
        assert "уже существует" in response_data["message"]
        assert "suggestion" in response_data

    async def test_get_accounts_success(
        self,
        client,
        saved_user,
        test_account_repo,
        faker: Faker,
    ):

        for i in range(5):
            new_acc = Account.create(
                user_id=saved_user.id.value,
                name=faker.word(),
                account_type=AccountType.CARD,
                balance=faker.pyfloat(positive=True),
                currency=AccountCurrency.RUB,
            )
            await test_account_repo.save(account=new_acc)

        response = await client.get(url=f"/api/v1/users/{saved_user.id.value}/accounts")

        assert response.status_code == 200
        assert len(response.json()["detail"]) == 5

    async def test_get_accounts_empty(
        self,
        client,
        saved_user,
        test_account_repo,
    ):
        response = await client.get(url=f"/api/v1/users/{saved_user.id.value}/accounts")

        assert response.status_code == 200
        assert len(response.json()["detail"]) == 0

    async def test_get_account_by_id_success(
        self,
        client,
        saved_user,
        faker: Faker,
        test_account_repo,
    ):
        account = Account.create(
            user_id=saved_user.id.value,
            name=faker.word(),
            balance=faker.pyfloat(positive=True),
            currency=AccountCurrency.RUB,
            account_type=AccountType.CASH,
        )
        await test_account_repo.save(account)

        response = await client.get(
            url=f"/api/v1/users/{saved_user.id.value}/accounts/{account.id.value}"
        )

        assert response.status_code == 200
        detail: dict = response.json()["detail"]

        assert detail["id"] == account.id.value
        assert detail["balance"] == account.balance
        assert detail["name"] == account.name.value
        assert "createdAt" in detail

    async def test_get_account_by_id_not_found(
        self,
        client,
        saved_user,
        test_account_repo,
    ):
        response = await client.get(
            url=f"/api/v1/users/{saved_user.id.value}/accounts/rand-acc-id"
        )

        assert response.status_code == 404
        assert "не найден" in response.json()["message"]
