from pydantic import BaseModel
from .base import BaseDTO
from typing import Optional


class Robot(BaseModel, BaseDTO):
    robot_name: str
    robot_desc: str
    robot_ip: str
    robot_status: Optional[int] = 1
    robot_map: Optional[str] = ""
