import logging
from typing import TypeVar

from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta

from category.models import Category
from category.schemas import CategoryCreate, CategoryResponse

Schema = TypeVar("Schema", bound=BaseModel, covariant=True)
SQLModel = TypeVar("SQLModel", bound=DeclarativeMeta, covariant=True)


class CategoryRepo:
    model = Category
    create_schema = CategoryCreate
    get_schema = CategoryResponse

    @classmethod
    async def update_category(cls, session: AsyncSession, user_id: int, **kwargs) -> Schema:
        clean_kwargs = {key: value for key, value in kwargs.items() if value is not None}
        await session.execute(update(Category).where(Category.user_id == user_id).values(**clean_kwargs))
        await session.commit()
        return await cls.get(session, user_id)

    @classmethod
    async def add_category(cls, session: AsyncSession, category: CategoryCreate):
        category_dict = category.model_dump()
        instance = Category(**category_dict)
        session.add(instance)
        await session.commit()
        await session.refresh(instance)
        logging.getLogger(__name__).info(instance.__dict__)
        return cls.get_schema.model_validate(instance)

    @classmethod
    async def get_users_category(cls, session: AsyncSession, user_id: int) -> list[Schema]:
        res = await session.execute(select(Category).filter_by(user_id=user_id))
        objects = res.scalars().all()
        print('ok')
        return [cls.get_schema.model_validate(obj) for obj in objects]

