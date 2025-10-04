from pydantic import BaseModel, Field
from .base import BaseDTO
from typing import Optional


class CallerBase(BaseModel):
    caller_name: str = Field(..., example="Caller 1")
    caller_ip: str = Field(..., example="192.168.0.1")
    caller_location: str = Field(..., example="Location A")
    caller_desc: str = Field(..., example="Caller in use for ...")
    caller_status: Optional[int] = 1
    # caller_additional_date: Optional[str] = Field(..., example="12/06/2025")
    caller_additional_date: Optional[str] = Field(
        default_factory=lambda: "", example="12/06/2025"
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


class CallerCreate(CallerBase, BaseDTO):
    pass


class CallerInDB(CallerBase):
    id: Optional[str] = Field(alias="_id", default=None)
