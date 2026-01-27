from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel


class AppConfig(BaseModel):
    title: str = "Funds Tracker API"
    debug: bool = True


class LogsConfig(BaseModel):
    level: Literal["DEBUG", "INFO", "WARNING"] = "INFO"
    format: str = "[%(asctime)s] - %(name)-26s - %(levelname)-7s - %(message)s"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
    )

    app: AppConfig = AppConfig()
    logs: LogsConfig = LogsConfig()


settings = Settings()
