from typing import Optional
from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    tg_id: int
    username: str
    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserCreate):
    tg_id: int
    username: Optional[str]

class UserFilter(BaseModel):
    tg_id: Optional[int]
    username: Optional[str]

class UserLogin(BaseModel):
    tg_id: int
    username: str
