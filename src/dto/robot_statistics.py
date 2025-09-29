from pydantic import BaseModel, Field
from typing import Dict, Optional
from datetime import date


class RobotStatistics(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    robot_id: str
    date: date
    runtime_hours: float = 0
    distance_traveled: float = 0
    error_count: int = 0
    # Cho phép key động
    status_distribution: Dict[str, int] = Field(default_factory=dict)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "robot_id": "Robot_01",
                "date": "2025-09-29",
                "runtime_hours": 1.5,
                "distance_traveled": 42.3,
                "error_count": 2,
                "status_distribution": {
                    "offline": 12,
                    "running": 33,
                    "idle": 5,
                    "charge": 2,
                    "alarm": 1,
                    "new_state": 7,  # có thể thêm bất kỳ key nào
                },
            }
        }
