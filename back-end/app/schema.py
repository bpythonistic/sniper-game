from uuid import uuid4, UUID

# from typing import Optional
from pydantic import BaseModel, Field


class User(BaseModel):
    id: UUID = Field(..., default_factory=uuid4)
    name: str
