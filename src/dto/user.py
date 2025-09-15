from .base import BaseDTO
from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Optional
from bson import ObjectId


class UserBase(BaseModel, BaseDTO):
    name: str
    email: EmailStr
    phone: str
    role_id: Optional[str] = ""  # lưu _id từ Role
    status: Literal[0, 1] = 1
    gender: Literal[0, 1] = 1


class UserCreate(UserBase):
    pass


class UserInDB(UserBase):
    id: str
