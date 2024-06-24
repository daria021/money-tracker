from typing import Optional

from pydantic import BaseModel, ConfigDict


class CategoryCreate(BaseModel):
    user_id: int
    title: str
    model_config = ConfigDict(from_attributes=True)


class CategoryResponse(CategoryCreate):
    id: int
    user_id: int
    title: str


class CategoryFilter(BaseModel):
    user_id: Optional[int]
    title: Optional[str]
