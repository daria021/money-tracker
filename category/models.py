from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
from wastes.models import Wastes


class Category(Base):
    __tablename__ = "category"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.tg_id"))
    title: Mapped[str] = mapped_column(unique=True)
    wastes: Mapped[list[Wastes]] = relationship(back_populates="category")

    def __repr__(self):
        return f"User @{self.username}"
