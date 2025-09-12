from pydantic import BaseModel
from .base import BaseDTO


class Robot(BaseModel, BaseDTO):
    robot_name: str
    robot_desc: str
    robot_ip: str
    robot_status: int
