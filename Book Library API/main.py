from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

from database import SessionLocal, engine, Base
from models import Book
from schemas import (
    BookCreate,
    BookResponse,
    BookUpdate
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Book Library API")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {"message": "Book Library API Running"}

@app.post("/books", response_model=BookResponse)
def create_book(
    book: BookCreate,
    db: Session = Depends(get_db)
):
    db_book = Book(**book.model_dump())

    db.add(db_book)
    db.commit()
    db.refresh(db_book)

    return db_book

@app.get("/books", response_model=list[BookResponse])
def get_books(
    search: str | None = None,
    genre: str | None = None,
    available: bool | None = None,
    sort: str = "title",
    page: int = 1,
    size: int = 10,
    db: Session = Depends(get_db)
):
    query = db.query(Book)

    if search:
        query = query.filter(
            or_(
                Book.title.ilike(f"%{search}%"),
                Book.author.ilike(f"%{search}%")
            )
        )

    if genre:
        query = query.filter(Book.genre == genre)

    if available is not None:
        query = query.filter(
            Book.available == available
        )

    if sort == "author":
        query = query.order_by(Book.author.asc())
    else:
        query = query.order_by(Book.title.asc())

    offset = (page - 1) * size

    return (
        query
        .offset(offset)
        .limit(size)
        .all()
    )

@app.get(
    "/books/{book_id}",
    response_model=BookResponse
)
def get_book(
    book_id: int,
    db: Session = Depends(get_db)
):
    book = (
        db.query(Book)
        .filter(Book.id == book_id)
        .first()
    )

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    return book


@app.put(
    "/books/{book_id}",
    response_model=BookResponse
)
def update_book(
    book_id: int,
    book_data: BookUpdate,
    db: Session = Depends(get_db)
):
    book = (
        db.query(Book)
        .filter(Book.id == book_id)
        .first()
    )

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    updates = book_data.model_dump(
        exclude_unset=True
    )

    for key, value in updates.items():
        setattr(book, key, value)

    db.commit()
    db.refresh(book)

    return book

@app.delete("/books/{book_id}")
def delete_book(
    book_id: int,
    db: Session = Depends(get_db)
):
    book = (
        db.query(Book)
        .filter(Book.id == book_id)
        .first()
    )

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    db.delete(book)
    db.commit()

    return {
        "message": "Book deleted successfully"
    }