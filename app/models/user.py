from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column()
    hash_password: Mapped[str | None] = mapped_column(nullable=True)
    provider: Mapped[str] = mapped_column()
    provider_id: Mapped[str] = mapped_column()