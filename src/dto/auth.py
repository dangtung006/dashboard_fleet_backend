from .base import BaseDTO
from pydantic import BaseModel, EmailStr, Field
from typing import Literal
from bson import ObjectId


class AuthBase(BaseModel):
    email: str
    password: str
