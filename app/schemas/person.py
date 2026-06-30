from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PersonCreate(BaseModel):
    external_id: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=100)
    gender: str | None = Field(default=None, max_length=20)
    department: str | None = Field(default=None, max_length=100)
    status: Literal["active", "inactive"] = "active"


class PersonRead(PersonCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
