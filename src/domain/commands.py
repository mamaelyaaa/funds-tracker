from dataclasses import dataclass, field


@dataclass(frozen=True)
class PaginationCommand:
    page: int = field(default=1)
    limit: int = field(default=10)

    @property
    def page_offset(self) -> int:
        return (self.page - 1) * self.limit
