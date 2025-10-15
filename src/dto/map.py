from .base import BaseDTO
from pydantic import BaseModel, Field
from typing import Optional
from .robot import Robot


class RobotMapBase(BaseModel):

    map_name: str = Field(..., example="industries map")
    map_desc: str = Field(..., example="industries map")
    map_json_data: str = Field(..., example="industries map")

    map_date: Optional[str] = Field(default_factory=lambda: "", example="12/06/2025")
    map_status: Optional[int] = 1
    robots_in_use: Optional[str] = Field(
        default_factory=lambda: "", example="68ba97b0530bf52840ff422c"
    )

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        json_schema_extra = {
            # "example": {
            #     "robot_id": "68dca231e07f5fcb86c61488",
            #     "date": "2025-09-29",
            #     "runtime_hours": 1.5,
            #     "distance_traveled": 42.3,
            #     "error_count": 2,
            #     "status_distribution": {
            #         "offline": 12,
            #         "running": 33,
            #         "idle": 5,
            #         "charge": 2,
            #         # "alarm": 1,
            #         # "new_state": 7,  # có thể thêm bất kỳ key nào
            #     },
            # }
        }


class RobotMapCreate(RobotMapBase):
    pass


class RobotMapInDB(RobotMapBase):
    id: Optional[str] = Field(alias="_id", default=None)
    robots_in_use: Robot
