from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Wastes(Base, AsyncAttrs):
    __tablename__ = "wastes"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.tg_id"))
    category_id: Mapped[str] = mapped_column(ForeignKey("category.id"))
    category: Mapped["Category"] = relationship(back_populates="wastes")
    amount: Mapped[int]
    date: Mapped[datetime]

    def __str__(self):
        return str({
            'id': self.id,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'category': self.category,
            'amount': self.amount,
            'date': self.date,
        })
