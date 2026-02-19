from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class DateMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )
    # updated_at: Mapped[datetime] = mapped_column(
    #     DateTime(timezone=True), onupdate=func.now()
    # )
