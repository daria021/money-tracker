from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

from category.schemas import CategoryResponse


class WastesCreate(BaseModel):
    user_id: int
    category: str
    amount: int
    date: datetime
    model_config = ConfigDict(from_attributes=True)


class WastesResponse(WastesCreate):
    user_id: int
    category: CategoryResponse
    amount: int
    date: datetime


class WastesFilter(BaseModel):
    user_id: Optional[int]
    category: Optional[str]
    amount: Optional[int]
    date: Optional[datetime]
