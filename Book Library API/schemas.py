from pydantic import BaseModel


class BookCreate(BaseModel):
    title: str
    author: str
    genre: str
    published_year: int


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    genre: str
    published_year: int
    available: bool

    class Config:
        from_attributes = True


class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    genre: str | None = None
    published_year: int | None = None
    available: bool | None = None