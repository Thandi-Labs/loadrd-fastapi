from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends, HTTPException, status, Path
from pydantic import BaseModel, Field

from models import Offers, OfferCategory
from .db import db_dependency
from .users import get_current_user

router = APIRouter(
    prefix="/offers",
    tags=["Offers"]
)

user_dependency = Annotated[dict, Depends(get_current_user)]


class OfferRequest(BaseModel):
    offer_name: str = Field(min_length=5, max_length=100)
    ussd: str = Field(min_length=3, max_length=100)
    amount: int = Field(gt=0, lt=10_000)
    active: bool
    category: OfferCategory


@router.get('/', status_code=status.HTTP_200_OK)
async def get_all_offers(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    return db.query(Offers).filter(Offers.user_id == user.get('id')).all()


@router.get("/offer/{offer_id}", status_code=status.HTTP_200_OK)
async def get_offer_by_id(user: user_dependency, db: db_dependency, offer_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")

    offer = db.query(Offers).filter(Offers.id == offer_id).filter(
        Offers.user_id == user.get('id')).first()

    if offer is not None:
        return offer
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Offer not found."
    )


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_offer(user: user_dependency, db: db_dependency, offer_request: OfferRequest):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")

    offer_model = Offers(**offer_request.model_dump(), user_id=user.get('id'))

    db.add(offer_model)
    db.commit()


@router.put('/update/{offer_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency, offer_id: int,
                      offer_request: OfferRequest):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")

    offer_model = db.query(Offers).filter(Offers.id == offer_id).filter(
        Offers.user_id == user.get('id')).first()

    if offer_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='offer not found')

    offer_model.offer_name = offer_request.offer_name
    offer_model.category = offer_request.category
    offer_model.amount = offer_request.amount
    offer_model.ussd = offer_request.ussd
    offer_model.active = offer_request.active

    db.add(offer_model)
    db.commit()


@router.delete('/delete/{offer_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_offer(user: user_dependency, db: db_dependency, offer_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")

    offer_model = db.query(Offers).filter(Offers.id == offer_id).filter(
        Offers.user_id == user.get('id')).first()

    if offer_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Offer not found')

    db.query(Offers).filter(Offers.id == offer_id).delete()
    db.commit()
