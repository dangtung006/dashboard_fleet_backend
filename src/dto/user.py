from .base import BaseDTO
from pydantic import BaseModel, EmailStr, Field
from typing import Literal
from bson import ObjectId


class UserBase(BaseModel, BaseDTO):
    name: str
    email: EmailStr
    phone: str
    gender: Literal[0, 1] = 1
    role_id: str  # lưu _id từ Role
    status: Literal[0, 1] = 1


class UserCreate(UserBase):
    pass


class UserInDB(UserBase):
    id: str
