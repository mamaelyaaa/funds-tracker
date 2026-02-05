import pytest

from domain.accounts.entity import Account
from domain.accounts.values import AccountCurrency, Title, AccountType


@pytest.mark.asyncio
@pytest.mark.api
class TestAccountApiCreation:

    async def test_success(self, client, test_user):
        response = await client.post(
            url=f"/api/v1/users/{test_user.id.value}/accounts",
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
        assert "created_at" in detail
        assert "id" in detail

    @pytest.mark.parametrize("account_name", [("%^%&$^#(%", "  ", "")])
    async def test_invalid_account_name(self, client, test_user, account_name):
        response = await client.post(
            url=f"/api/v1/users/{test_user.id.value}/accounts",
            json={
                "name": account_name,
                "initial_balance": 1000,
                "currency": "RUB",
                "account_type": "Card",
            },
        )
        assert response.status_code in (400, 422)

    async def test_account_already_exists(self, client, test_user, test_account_repo):
        account = Account.create(
            user_id=test_user.id,
            name=Title("Новый счет"),
            balance=2000,
            currency=AccountCurrency.RUB,
            account_type=AccountType.CARD,
        )
        await test_account_repo.save(account)

        response = await client.post(
            url=f"/api/v1/users/{test_user.id.value}/accounts",
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
