from .base import BaseDTO
from pydantic import BaseModel, EmailStr, Field
from typing import Literal
from bson import ObjectId


class UserActionBase(BaseModel):
    created_at: int
    expireAt: int
    token_id: str
    user_id: str


class UserActionCreate(UserActionBase):
    pass


class UserActionInDB(UserActionBase):
    id: str
