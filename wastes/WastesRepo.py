import logging
from typing import TypeVar

from pydantic import BaseModel
from sqlalchemy import select, extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta

from category import Category
from wastes.models import Wastes
from wastes.schemas import WastesCreate, WastesResponse



Schema = TypeVar("Schema", bound=BaseModel, covariant=True)
SQLModel = TypeVar("SQLModel", bound=DeclarativeMeta, covariant=True)


class WastesRepo:
    model = Wastes
    create_schema = WastesCreate
    get_schema = WastesResponse

    @classmethod
    async def waste_one_month(cls, session: AsyncSession, user_id: int, month: int) -> Schema:
        res = await session.execute(
            select(Wastes).where(
                Wastes.user_id == user_id,
                extract('month', Wastes.date) == month
            )
        )
        objects = res.scalars().all()
        for obj in objects:
            await obj.awaitable_attrs.category
        return [cls.get_schema.model_validate(obj) for obj in objects]

    @classmethod
    async def add_waste(cls, session: AsyncSession, wastes: WastesCreate) -> WastesResponse:

        category = (await session.execute(select(Category).where(Category.title == wastes.category))).scalar_one()
        wastes_dict = wastes.model_dump()
        wastes_dict["category"] = category
        instance = Wastes(**wastes_dict)
        session.add(instance)
        await session.commit()
        await session.refresh(instance)
        logging.getLogger(__name__).info(instance.__dict__)
        return cls.get_schema.model_validate(instance)


