from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends, HTTPException, status
from pydantic import BaseModel
from datetime import date

from models import Transactions, TransactionStatusTypes
from .db import db_dependency
from .users import get_current_user

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)


class CreateTransactionRequest(BaseModel):
    user_id: str
    offer_id: str
    customer_name: str
    customer_phone: str
    amount: str
    status: TransactionStatusTypes
    created_at: date


user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/", status_code=status.HTTP_200_OK)
async def get_transactions(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    return db.query(Transactions).filter(Transactions.user_id == user.get('id')).all()


@router.post("/create-transaction", status_code=status.HTTP_201_CREATED)
async def create_transaction(user: user_dependency, db: db_dependency, transaction: CreateTransactionRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    transaction = Transactions(**transaction.model_dump(), user_id=user.get("id"))
    db.add(transaction)
    db.commit()