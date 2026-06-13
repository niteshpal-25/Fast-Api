from datetime import datetime
from pydantic import BaseModel


class NoteCreate(BaseModel):
    title: str
    content: str
    tag: str | None = None


class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    tag: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    tag: str | None = None