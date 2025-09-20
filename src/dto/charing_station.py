from .base import BaseDTO
from pydantic import BaseModel, Field
from typing import Optional, Optional



class CharingStationBase(BaseModel):
    
    charing_station_name: str = Field(..., example="industries map")
    charing_station_desc: str = Field(..., example="industries map")
    charing_station_location: str = Field(..., example="industries map")
    map_status: Optional[int] = 1
    charing_station_additional_date: str = Field(..., example="12/06/2025")


class CharingStationCreate(CharingStationBase):
    pass


class CharingStationInDB(CharingStationBase):
    id: str
