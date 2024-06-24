import logging
from typing import TypeVar, Type

from pydantic import BaseModel
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta

from category import Category
from user import User
from user.schemas import UserResponse
from wastes.models import Wastes

Schema = TypeVar("Schema", bound=BaseModel, covariant=True)
SQLModel = TypeVar("SQLModel", bound=DeclarativeMeta, covariant=True)

class AbstractRepo:
    model: Type[SQLModel]
    update_schema: Type[Schema]
    create_schema: Type[Schema]
    get_schema: Type[Schema]

    async def get_user(cls, session: AsyncSession, user_id: int) -> UserResponse | None:
        res = await session.execute(select(User).where(User.id == user_id))
        obj = res.scalar_one()
        return cls.get_schema.model_validate(obj) if obj else None

    async def get_all_users(cls, session: AsyncSession, *filters, offset: int = 0, limit: int = 100) -> list[Schema]:
        res = await session.execute(select(User).offset(offset).limit(limit).where(*filters))
        objects = res.scalars().all()
        return [cls.get_schema.model_validate(obj) for obj in objects]

    async def get_user_filtered_by(cls, session: AsyncSession, **kwargs) -> list[Schema]:
        res = await session.execute(select(User).filter_by(**kwargs))
        objects = res.scalars().all()
        # print([obj.m for obj in objects])
        return [cls.get_schema.model_validate(obj) for obj in objects]

    async def create_user(cls, session: AsyncSession, **kwargs) -> Schema:
        instance = User(**kwargs)
        session.add(instance)
        await session.commit()
        await session.refresh(instance)
        logging.getLogger(__name__).info(instance.__dict__)
        return cls.get_schema.model_validate(instance)


    async def delete_user(cls, session: AsyncSession, user_id: int):
        await session.execute(delete(User).where(User.id == user_id))
        await session.commit()

    async def update_category(cls, session: AsyncSession, user_id: int, **kwargs) -> Schema:
        clean_kwargs = {key: value for key, value in kwargs.items() if value is not None}
        await session.execute(update(Category).where(Category.user_id == user_id).values(**clean_kwargs))
        await session.commit()
        return await cls.get(session, user_id)

    async def waste_one_month(cls, session: AsyncSession, user_id: int, month: int) -> Schema:
        res = await session.execute(select(Wastes).filter_by(Wastes.date.month == month))
        objects = res.scalars().all()
        # print([obj.m for obj in objects])
        return [cls.get_schema.model_validate(obj) for obj in objects]
