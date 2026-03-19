from datetime import timedelta, datetime, UTC, timezone
from pathlib import Path
from typing import Literal

from authx.types import AlgorithmType

from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from domain.histories.values import HistoryInterval, HistoryPeriod

load_dotenv()


class RunConfig(BaseModel):
    port: int = 8000
    workers: int = 1

    @property
    def URL(self) -> str:
        return f"http://localhost:{self.port}"


class AppConfig(BaseModel):
    title: str = "Funds Tracker API"
    debug: bool = True
    env: Literal["DEV", "TEST"] = "DEV"


class FilesConfig(BaseModel):
    base: Path = Path(__file__).parent.parent.parent
    src: Path = base / "src"

    env: Path = base / ".env"
    env_example: Path = base / ".env.example"

    test_db: Path = base / "tests" / "test.db"


class LogsConfig(BaseModel):
    level: Literal["DEBUG", "INFO", "WARNING"] = "INFO"
    format: str = "[%(asctime)s] - %(name)-20s - %(levelname)-7s - %(message)s"


class SQLAlchemyConfig(BaseModel):
    echo: bool = False
    pool_size: int = 20
    max_overflow: int = 30

    intervals: dict[HistoryInterval, tuple[datetime, HistoryPeriod]] = {
        HistoryInterval.DAY: (
            datetime.now(UTC) - relativedelta(days=1),
            HistoryPeriod.MINUTES,
        ),
        HistoryInterval.WEEK1: (
            datetime.now(timezone.utc) - relativedelta(weeks=1),
            HistoryPeriod.HOURS,
        ),
        HistoryInterval.MONTH1: (
            datetime.now(timezone.utc) - relativedelta(months=1),
            HistoryPeriod.DAYS,
        ),
        HistoryInterval.MONTH6: (
            datetime.now(timezone.utc) - relativedelta(months=6),
            HistoryPeriod.WEEKS,
        ),
        HistoryInterval.YEAR: (
            datetime.now(timezone.utc) - relativedelta(years=1),
            HistoryPeriod.MONTHS,
        ),
        HistoryInterval.ALL_TIME: (
            datetime(2000, 1, 1),
            HistoryPeriod.YEARS,
        ),
    }

    def start_date(self, interval: HistoryInterval) -> datetime:
        return self.intervals[interval][0]

    def period(self, interval: HistoryInterval) -> HistoryPeriod:
        return self.intervals[interval][1]


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

    @property
    def AIOSQLITE_TEST_DSN(self) -> str:
        return f"sqlite+aiosqlite:///{settings.files.test_db.as_posix()}"


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

    result_backend_ex_time: int = timedelta(minutes=2).total_seconds()


class CacheConfig(BaseModel):
    port: int
    host: str

    @property
    def REDIS_DSN(self, db_index: int = 0) -> str:
        return f"redis://{self.host}:{self.port}/{db_index}"


class JWTConfig(BaseModel):
    algorithm: AlgorithmType = "HS256"
    secret: str = "jwt-secret"


class Settings(BaseSettings):
    db: DBConfig
    broker: BrokerConfig
    cache: CacheConfig
    jwt: JWTConfig

    run: RunConfig = RunConfig()
    app: AppConfig = AppConfig()
    files: FilesConfig = FilesConfig()
    logs: LogsConfig = LogsConfig()

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        case_sensitive=False,
        env_file=(files.env_example, files.env),
    )


settings = Settings()  # noqa
