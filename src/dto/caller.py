from pydantic import BaseModel, Field
from .base import BaseDTO
from typing import Optional


class CallerBase(BaseModel, BaseDTO):
    caller_name: str = Field(..., example="industries map")
    caller_ip: str = Field(..., example="192.168.0.1")
    caller_location: str = Field(..., example="HCM")
    caller_desc: str = Field(..., example="industries map")
    caller_status: Optional[int] = 1
    call_additional_date: str = Field(..., example="12/06/2025")


class CallerCreate(CallerBase):
    pass


class CallerInDB(CallerBase):
    id: str
