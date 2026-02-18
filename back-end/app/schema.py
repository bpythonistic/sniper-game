from pydantic import BaseModel, Field
# from typing import Optional
from uuid import uuid4, UUID

class User(BaseModel):
    id: UUID = Field(..., default_factory=uuid4)
    name: str
