from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

from database import SessionLocal, engine, Base
from models import Note
from schemas import (
    NoteCreate,
    NoteResponse,
    NoteUpdate
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Notes API")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {"message": "Notes API Running"}


# CREATE NOTE
@app.post("/notes", response_model=NoteResponse)
def create_note(
    note: NoteCreate,
    db: Session = Depends(get_db)
):
    db_note = Note(
        title=note.title,
        content=note.content,
        tag=note.tag
    )

    db.add(db_note)
    db.commit()
    db.refresh(db_note)

    return db_note


# GET ALL NOTES
@app.get("/notes", response_model=list[NoteResponse])
def get_notes(
    search: str | None = None,
    tag: str | None = None,
    sort: str = "desc",
    page: int = 1,
    size: int = 10,
    db: Session = Depends(get_db)
):
    query = db.query(Note)

    # Search
    if search:
        query = query.filter(
            or_(
                Note.title.ilike(f"%{search}%"),
                Note.content.ilike(f"%{search}%")
            )
        )

    # Filter by tag
    if tag:
        query = query.filter(Note.tag == tag)

    # Sort by date
    if sort == "asc":
        query = query.order_by(Note.created_at.asc())
    else:
        query = query.order_by(Note.created_at.desc())

    # Pagination
    offset = (page - 1) * size

    notes = (
        query
        .offset(offset)
        .limit(size)
        .all()
    )

    return notes


# GET SINGLE NOTE
@app.get("/notes/{note_id}", response_model=NoteResponse)
def get_note(
    note_id: int,
    db: Session = Depends(get_db)
):
    note = (
        db.query(Note)
        .filter(Note.id == note_id)
        .first()
    )

    if not note:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    return note


# UPDATE NOTE
@app.put("/notes/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: int,
    note_data: NoteUpdate,
    db: Session = Depends(get_db)
):
    note = (
        db.query(Note)
        .filter(Note.id == note_id)
        .first()
    )

    if not note:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    updates = note_data.model_dump(
        exclude_unset=True
    )

    for key, value in updates.items():
        setattr(note, key, value)

    db.commit()
    db.refresh(note)

    return note


# DELETE NOTE
@app.delete("/notes/{note_id}")
def delete_note(
    note_id: int,
    db: Session = Depends(get_db)
):
    note = (
        db.query(Note)
        .filter(Note.id == note_id)
        .first()
    )

    if not note:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    db.delete(note)
    db.commit()

    return {"message": "Note deleted successfully"}