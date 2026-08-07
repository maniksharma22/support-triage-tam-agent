from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class DocumentCreate(BaseModel):
    title: str
    content: str
    tags: Optional[List[str]] = []

class DocumentResponse(BaseModel):
    id: int
    title: str
    content: str
    tags: List[str] = []
    created_at: datetime

    class Config:
        from_attributes = True