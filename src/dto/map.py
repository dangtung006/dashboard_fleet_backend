from .base import BaseDTO
from pydantic import BaseModel, Field
from typing import Optional


class RobotMapBase(BaseModel):

    map_name: str = Field(..., example="industries map")
    map_desc: str = Field(..., example="industries map")
    map_json_data: str = Field(..., example="industries map")

    map_date: Optional[str] = Field(default_factory=lambda: "", example="12/06/2025")
    map_status: Optional[int] = 1
    robots_in_use: Optional[str] = Field(
        default_factory=lambda: "", example="68ba97b0530bf52840ff422c"
    )


class RobotMapCreate(RobotMapBase):
    pass


class RobotMapInDB(RobotMapBase):
    id: str
