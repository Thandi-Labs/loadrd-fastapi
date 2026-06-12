from fastapi import APIRouter
from pydantic import BaseModel, Field

from models import Offers, OfferCategory
from database import SessionLocal

from typing import Annotated

from fastapi import Depends, HTTPException, status, Path
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/offers",
    tags=["Offers"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class OfferRequest(BaseModel):
    offer_name: str = Field(min_length=5, max_length=100)
    ussd: str = Field(min_length=3, max_length=100)
    amount: int = Field(gt=0, lt=10_000)
    active: bool
    category: OfferCategory


db_dependency = Annotated[Session, Depends(get_db)]


@router.get('/', status_code=status.HTTP_200_OK)
async def get_all_offers(db: db_dependency):
    return db.query(Offers).all()


@router.get("/offer/{offer_id}", status_code=status.HTTP_200_OK)
async def get_offer_by_id(db: db_dependency, offer_id: int = Path(gt=0)):
    offer = db.query(Offers).filter(Offers.id == offer_id).first()
    if offer is not None:
        return offer
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Offer not found."
    )


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_offer(db: db_dependency, offer_request: OfferRequest):
    offer_model = Offers(**offer_request.model_dump())

    db.add(offer_model)
    db.commit()


@router.put('/update/{offer_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency, offer_id: int,
                      offer_request: OfferRequest):
    offer_model = db.query(Offers).filter(Offers.id == offer_id).first()

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
async def delete_offer(db: db_dependency, offer_id: int = Path(gt=0)):
    offer_model = db.query(Offers).filter(Offers.id == offer_id).first()

    if offer_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Offer not found')

    db.query(Offers).filter(Offers.id == offer_id).delete()
    db.commit()
