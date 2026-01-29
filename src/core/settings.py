from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, AmqpDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class AppConfig(BaseModel):
    title: str = "Funds Tracker API"
    debug: bool = True
    env: Literal["DEV", "TEST"] = "DEV"


class FilesConfig(BaseModel):
    base: Path = Path(__file__).parent.parent.parent
    src: Path = base / "src"

    env: Path = base / ".env"
    env_example: Path = base / ".env.example"


class LogsConfig(BaseModel):
    level: Literal["DEBUG", "INFO", "WARNING"] = "INFO"
    format: str = "[%(asctime)s] - %(name)-29s - %(levelname)-7s - %(message)s"


class SQLAlchemyConfig(BaseModel):
    echo: bool = False


class DBConfig(BaseModel):
    user: str
    password: str
    port: int
    host: str
    name: str

    sqla: SQLAlchemyConfig = SQLAlchemyConfig()

    @property
    def POSTGRES_DSN(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class BrokerConfig(BaseModel):
    user: str
    password: str
    port: int
    host: str
    vhost: str = ""

    @property
    def AMQP_DSN(self) -> str:
        return (
            f"amqp://{self.user}:{self.password}@{self.host}:{self.port}/{self.vhost}"
        )


class Settings(BaseSettings):
    db: DBConfig
    broker: BrokerConfig
    app: AppConfig = AppConfig()
    files: FilesConfig = FilesConfig()
    logs: LogsConfig = LogsConfig()

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        case_sensitive=False,
        env_file=(files.env_example, files.env),
    )


settings = Settings()  # type: ignore
