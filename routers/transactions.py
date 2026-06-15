from fastapi import APIRouter

from models import Transactions, TransactionStatusTypes
from .db import db_dependency

from .users import get_current_user

from typing import Annotated

from fastapi import Depends, HTTPException, status, Path

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)

user_dependency = Annotated[dict, Depends(get_current_user)]


@app.get("/", status_code=status.HTTP_200_OK)
async def get_transactions(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    return db.query(Transactions).filter(Transactions.user_id == user.get('id')).all()
