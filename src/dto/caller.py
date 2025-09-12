from pydantic import BaseModel
from .base import BaseDTO


class Caller(BaseModel, BaseDTO):
    caller_name: str
    caller_ip: str
    caller_location: str
    caller_desc: str
    caller_status: int
