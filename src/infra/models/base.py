import uuid

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    id: Mapped[str] = mapped_column(primary_key=True, default=str(uuid.uuid4()))
