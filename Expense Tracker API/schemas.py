from datetime import datetime
from pydantic import BaseModel


class ExpenseCreate(BaseModel):
    title: str
    amount: float
    category: str
    description: str | None = None


class ExpenseResponse(BaseModel):
    id: int
    title: str
    amount: float
    category: str
    description: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class ExpenseUpdate(BaseModel):
    title: str | None = None
    amount: float | None = None
    category: str | None = None
    description: str | None = None