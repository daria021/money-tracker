import logging
from typing import TypeVar

from pydantic import BaseModel
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta

from user.models import User
from user.schemas import UserResponse, UserCreate

Schema = TypeVar("Schema", bound=BaseModel, covariant=True)
SQLModel = TypeVar("SQLModel", bound=DeclarativeMeta, covariant=True)


class UserRepo:
    model = User
    create_schema = UserCreate
    get_schema = UserResponse

    @classmethod
    async def get_user(cls, session: AsyncSession, user_id: int) -> UserResponse | None:
        res = await session.execute(select(User).where(User.tg_id == user_id))
        obj = res.scalar_one()
        return cls.get_schema.model_validate(obj) if obj else None
    @classmethod
    async def get_all_users(cls, session: AsyncSession, *filters, offset: int = 0, limit: int = 100) -> list[Schema]:
        res = await session.execute(select(User).offset(offset).limit(limit).where(*filters))
        objects = res.scalars().all()
        return [cls.get_schema.model_validate(obj) for obj in objects]

    @classmethod
    async def get_user_filtered_by(cls, session: AsyncSession, **kwargs) -> list[Schema]:
        res = await session.execute(select(User).filter_by(**kwargs))
        objects = res.scalars().all()
        # print([obj.m for obj in objects])
        return [cls.get_schema.model_validate(obj) for obj in objects]

    @classmethod
    async def create_user(cls, session: AsyncSession,user: UserCreate) -> Schema:
        instance = User(**user.model_dump())
        session.add(instance)
        await session.commit()
        await session.refresh(instance)
        logging.getLogger(__name__).info(instance.__dict__)
        return cls.get_schema.model_validate(instance)

    @classmethod
    async def delete_user(cls, session: AsyncSession, user_id: int):
        await session.execute(delete(User).where(User.id == user_id))
        await session.commit()


