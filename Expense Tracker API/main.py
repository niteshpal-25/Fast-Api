from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

from database import SessionLocal, engine, Base
from models import Expense
from schemas import (
    ExpenseCreate,
    ExpenseResponse,
    ExpenseUpdate
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Expense Tracker API")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {"message": "Expense Tracker API Running"}


# CREATE EXPENSE
@app.post("/expenses", response_model=ExpenseResponse)
def create_expense(
    expense: ExpenseCreate,
    db: Session = Depends(get_db)
):
    db_expense = Expense(**expense.model_dump())

    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)

    return db_expense


# GET ALL EXPENSES
@app.get("/expenses", response_model=list[ExpenseResponse])
def get_expenses(
    search: str | None = None,
    category: str | None = None,
    sort: str = "date",
    page: int = 1,
    size: int = 10,
    db: Session = Depends(get_db)
):
    query = db.query(Expense)

    if search:
        query = query.filter(
            or_(
                Expense.title.ilike(f"%{search}%"),
                Expense.description.ilike(f"%{search}%")
            )
        )

    if category:
        query = query.filter(
            Expense.category == category
        )

    if sort == "amount":
        query = query.order_by(
            Expense.amount.desc()
        )
    else:
        query = query.order_by(
            Expense.created_at.desc()
        )

    offset = (page - 1) * size

    return (
        query
        .offset(offset)
        .limit(size)
        .all()
    )


# GET SINGLE EXPENSE
@app.get(
    "/expenses/{expense_id}",
    response_model=ExpenseResponse
)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db)
):
    expense = (
        db.query(Expense)
        .filter(Expense.id == expense_id)
        .first()
    )

    if not expense:
        raise HTTPException(
            status_code=404,
            detail="Expense not found"
        )

    return expense


# UPDATE EXPENSE
@app.put(
    "/expenses/{expense_id}",
    response_model=ExpenseResponse
)
def update_expense(
    expense_id: int,
    expense_data: ExpenseUpdate,
    db: Session = Depends(get_db)
):
    expense = (
        db.query(Expense)
        .filter(Expense.id == expense_id)
        .first()
    )

    if not expense:
        raise HTTPException(
            status_code=404,
            detail="Expense not found"
        )

    updates = expense_data.model_dump(
        exclude_unset=True
    )

    for key, value in updates.items():
        setattr(expense, key, value)

    db.commit()
    db.refresh(expense)

    return expense


# DELETE EXPENSE
@app.delete("/expenses/{expense_id}")
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db)
):
    expense = (
        db.query(Expense)
        .filter(Expense.id == expense_id)
        .first()
    )

    if not expense:
        raise HTTPException(
            status_code=404,
            detail="Expense not found"
        )

    db.delete(expense)
    db.commit()

    return {
        "message": "Expense deleted successfully"
    }