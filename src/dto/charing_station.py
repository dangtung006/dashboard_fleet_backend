from .base import BaseDTO
from pydantic import BaseModel, Field
from typing import Optional


class CharingStationBase(BaseModel):

    charing_station_name: str = Field(..., example="Tram sac 1")
    charing_station_desc: str = Field(..., example="Tram sac cho robot")
    charing_station_location: str = Field(..., example="A1-01")
    charing_station_additional_date: Optional[str] = Field(
        default_factory=lambda: "", example="12/06/2025"
    )
    charing_status: Optional[int] = 1

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        json_schema_extra = {}


class CharingStationCreate(CharingStationBase, BaseDTO):
    pass


class CharingStationInDB(CharingStationBase):
    id: Optional[str] = Field(alias="_id", default=None)
