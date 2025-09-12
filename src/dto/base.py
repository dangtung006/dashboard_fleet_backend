from datetime import datetime
from pydantic import Field


class BaseDTO:
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
