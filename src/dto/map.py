from .base import BaseDTO
from pydantic import BaseModel, Field
from typing import Optional, Optional


class MapBase(BaseModel):

    map_name: str = Field(..., example="industries map")
    map_desc: str = Field(..., example="industries map")
    map_json_data: str = Field(..., example="industries map")

    map_date: Optional[str] = Field(default_factory=lambda: "", example="12/06/2025")
    map_status: Optional[int] = 1


class MapCreate(MapBase, BaseDTO):
    pass


class MapInDB(MapBase):
    id: str
