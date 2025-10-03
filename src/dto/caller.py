from pydantic import BaseModel, Field
from .base import BaseDTO
from typing import Optional


class CallerBase(BaseModel, BaseDTO):
    caller_name: str = Field(..., example="Caller 1")
    caller_ip: str = Field(..., example="192.168.0.1")
    caller_location: str = Field(..., example="Location A")
    caller_desc: str = Field(..., example="Caller in use for ...")
    caller_status: Optional[int] = 1
    caller_additional_date: str = Field(..., example="12/06/2025")


class CallerCreate(CallerBase):
    pass


class CallerInDB(CallerBase):
    id: str
