from .base import BaseDTO
from pydantic import BaseModel, EmailStr, Field
from typing import Literal
from bson import ObjectId


class UserBase(BaseModel, BaseDTO):
    name: str
    email: EmailStr
    role_id: str  # lưu _id từ Role
    status: Literal["active", "inactive"] = "active"


class UserCreate(UserBase):
    pass


class UserInDB(UserBase):
    id: str
