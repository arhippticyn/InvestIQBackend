from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .finances import Expense, Income


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True)
    hash_password: Mapped[str | None] = mapped_column(nullable=True)
    provider: Mapped[str] = mapped_column()
    provider_id: Mapped[str] = mapped_column()
    budget: Mapped[int] = mapped_column(default=0)

    expenses: Mapped[List['Expense']] = relationship(back_populates='user')
    incomes: Mapped[List['Income']] = relationship(back_populates='user')