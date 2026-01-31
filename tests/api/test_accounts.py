import pytest

from accounts.values import AccountType, AccountCurrency
from api.v1.schemas.accounts import CreateAccountSchema
from users.domain import User
from users.values import UserId


@pytest.fixture
async def test_user(test_user_repository):
    user_id = UserId("u-123")
    user = User(id=user_id, name="user")
    await test_user_repository.save(user)

    saved_user = await test_user_repository.get_by_id(user.id)
    assert saved_user is not None
    assert saved_user.id.value == "u-123"

    return user


@pytest.mark.asyncio
async def test_account_api_create(client, test_user):
    schema = CreateAccountSchema(
        name="Накопительный",
        initial_balance=3000,
        account_type=AccountType.CARD,
        currency=AccountCurrency.RUB,
    )

    resp = await client.post(
        url=f"/api/v1/users/{test_user.id.value}/accounts",
        json=schema.model_dump(),
    )

    assert resp.status_code == 201
    data = resp.json()

    assert data.get("message") == f"Счет '{schema.name}' успешно создан"
    assert data.get("metadata") == {}
    assert data.get("detail") is not None
    assert "accountId" in data.get("detail")
