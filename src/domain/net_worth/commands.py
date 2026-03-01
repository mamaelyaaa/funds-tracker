from dataclasses import dataclass

from domain.histories.values import HistoryInterval


@dataclass(frozen=True)
class GetByIntervals:
    user_id: str
    interval: HistoryInterval
