from fastapi import APIRouter

router = APIRouter(
    prefix="/offers",
    tags=["Offers"]
)


@router.get("/")
def get_offers():
    return {"offers": [{"id": "OFFER20", "discount": "20%"}]}


@router.get("/{offer_id}")
def get_offer(offer_id: str):
    return {"offer_id": offer_id, "discount": "20%"}
