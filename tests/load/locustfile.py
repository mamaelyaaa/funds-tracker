from locust import HttpUser, task, between

from src.core.config import settings


class AccountUser(HttpUser):
    wait_time = between(0.1, 0.5)  # Пауза между запросами
    host = settings.run.URL

    @task
    def get_accounts(self):
        self.client.get("/api/v1/users/1a3f28ed-19f2-4b67-beaf-b1b173165049/accounts")

    # @task
    # def update_balance(self):
    #     self.client.put(
    #         "/api/v1/users/1a3f28ed-19f2-4b67-beaf-b1b173165049"
    #         "/accounts/afffc41e-bc03-4d0f-a687-c7a8d54eacb8/balance",
    #         json={"actual_balance": random.randint(100, 10000)},
    #     )
