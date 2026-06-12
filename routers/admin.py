from fastapi import APIRouter
from pydantic import BaseModel, Field

from models import Offers, OfferCategory
from .db import db_dependency

from .users import get_current_user, RoleTypes

from typing import Annotated

from fastapi import Depends, HTTPException, status, Path
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/admin",
    tags=["Administrator"]
)

user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get('/offers', status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None or user.get('role') != RoleTypes.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication failed'
        )
    return db.query(Offers).all()


@router.delete("/delete/{offer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_offer(user: user_dependency, db: db_dependency, offer_id: int = Path(gt=0)):
    if user is None or user.get('role') != RoleTypes.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication failed'
        )

    offer_model = db.query(Offers).filter(Offers.id == offer_id).first()

    if offer_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Offer not found')

    db.query(Offers).filter(Offers.id == offer_id).delete()
    db.commit()
