from .base import BaseDTO
from pydantic import BaseModel, Field
from typing import Optional, Optional


class PermisionUpdate(BaseModel):
    resource: str
    action: str
    val: bool


class MapBase(BaseModel):
    map_name: str = Field(..., example="industries map")
    map_status: Optional[int] = 1
    map_desc: str = Field(..., example="industries map")
    map_json_data: str = Field(..., example="industries map")
    map_date: str = Field(..., example="12/06/2025")


class MapCreate(MapBase):
    pass


class MapInDB(MapBase):
    id: str
