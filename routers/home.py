from typing import Annotated

from fastapi import APIRouter, Path
from fastapi import Depends, HTTPException, status
from pydantic import BaseModel
from datetime import date

from models import Transactions, TransactionStatusTypes
from .db import db_dependency
from .users import get_current_user

router = APIRouter(
    prefix="/home",
    tags=["Dashboard"]
)

user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/stats/", status_code=status.HTTP_200_OK)
async def get_dashboard(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    return db.query(Transactions).filter(Transactions.user_id == user.get('id')).all()
