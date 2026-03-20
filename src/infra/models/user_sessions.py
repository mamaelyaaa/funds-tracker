from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, DateTime, CheckConstraint, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infra.models import Base
from infra.models.mixin import TimeStampMixin

if TYPE_CHECKING:
    from . import UserModel


class UserSessionModel(Base, TimeStampMixin):
    __tablename__ = "user_sessions"

    user_id: Mapped[str] = mapped_column(
        ForeignKey(
            "users.id",
            name="fk_us_user_id",
            ondelete="CASCADE",
        )
    )
    refresh_jti: Mapped[str] = mapped_column(unique=True)
    expires_in: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    fingerprint: Mapped[str] = mapped_column(index=True)

    # Отношения
    user: Mapped["UserModel"] = relationship(back_populates="sessions")

    # Консистентность
    __table_args__ = (
        CheckConstraint("created_at <= expires_in", name="session_date_constraint"),
        UniqueConstraint(
            "fingerprint", "user_id", name="session_user_fingerprint_constraint"
        ),
        # Index("session_user_id_exp_idx", "user_id", "expires_in"),
    )
