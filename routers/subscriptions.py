from datetime import datetime, timedelta

from fastapi import APIRouter
from fastapi import HTTPException, status, Path
from pydantic import BaseModel, Field

from models import Subscriptions, UserSubscriptions, RoleTypes, Users
from .db import db_dependency
from .users import user_dependency

router = APIRouter(
    prefix="/subscriptions",
    tags=["Subscriptions"]
)


class SubscriptionRequest(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    description: str = Field(min_length=5, max_length=255)
    request_count: int = Field(gt=0)
    price: int = Field(gt=0, lt=100_000)
    duration_days: int = Field(gt=0, lt=366)
    active: bool


@router.get('/', status_code=status.HTTP_200_OK)
async def get_all_subscriptions(db: db_dependency):
    return db.query(Subscriptions).filter(Subscriptions.active == True).all()


@router.get('/my-subscription', status_code=status.HTTP_200_OK)
async def get_my_subscription(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")

    user_subscription = db.query(UserSubscriptions).filter(
        UserSubscriptions.user_id == user.get('id')).filter(
        UserSubscriptions.expiry_date >= datetime.now()).first()

    if user_subscription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No active subscription found')

    return user_subscription


@router.put('/consume-token', status_code=status.HTTP_200_OK)
async def consume_token(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")

    user_subscription = db.query(UserSubscriptions).filter(
        UserSubscriptions.user_id == user.get('id')).filter(
        UserSubscriptions.expiry_date >= datetime.now()).first()

    if user_subscription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No active subscription found')

    if user_subscription.requests_remaining <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='No tokens remaining on your subscription')

    user_subscription.requests_remaining -= 1

    db.add(user_subscription)
    db.commit()

    return {'requests_remaining': user_subscription.requests_remaining}


@router.get('/{subscription_id}', status_code=status.HTTP_200_OK)
async def get_subscription_by_id(db: db_dependency, subscription_id: int = Path(gt=0)):
    subscription = db.query(Subscriptions).filter(
        Subscriptions.id == subscription_id).first()

    if subscription is not None:
        return subscription
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Subscription not found."
    )


@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_subscription(user: user_dependency, db: db_dependency,
                              subscription_request: SubscriptionRequest):
    if user is None or user.get('role') != RoleTypes.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")

    subscription_model = Subscriptions(**subscription_request.model_dump())

    db.add(subscription_model)
    db.commit()


@router.put('/update/{subscription_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_subscription(user: user_dependency, db: db_dependency,
                              subscription_request: SubscriptionRequest,
                              subscription_id: int = Path(gt=0)):
    if user is None or user.get('role') != RoleTypes.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")

    subscription_model = db.query(Subscriptions).filter(
        Subscriptions.id == subscription_id).first()

    if subscription_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Subscription not found')

    subscription_model.name = subscription_request.name
    subscription_model.description = subscription_request.description
    subscription_model.request_count = subscription_request.request_count
    subscription_model.price = subscription_request.price
    subscription_model.duration_days = subscription_request.duration_days
    subscription_model.active = subscription_request.active

    db.add(subscription_model)
    db.commit()


@router.put('/deactivate/{subscription_id}', status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_subscription(user: user_dependency, db: db_dependency,
                                  subscription_id: int = Path(gt=0)):
    if user is None or user.get('role') != RoleTypes.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")

    subscription_model = db.query(Subscriptions).filter(
        Subscriptions.id == subscription_id).first()

    if subscription_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Subscription not found')

    subscription_model.active = not subscription_model.active
    db.add(subscription_model)
    db.commit()


@router.delete('/delete/{subscription_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_subscription(user: user_dependency, db: db_dependency,
                              subscription_id: int = Path(gt=0)):
    if user is None or user.get('role') != RoleTypes.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")

    subscription_model = db.query(Subscriptions).filter(
        Subscriptions.id == subscription_id).first()

    if subscription_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Subscription not found')

    has_purchases = db.query(UserSubscriptions).filter(
        UserSubscriptions.subscription_id == subscription_id).first()

    if has_purchases is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Subscription has purchases and cannot be deleted. Deactivate it instead.')

    db.query(Subscriptions).filter(
        Subscriptions.id == subscription_id).delete()
    db.commit()


@router.post('/purchase/{subscription_id}', status_code=status.HTTP_201_CREATED)
async def purchase_subscription(user: user_dependency, db: db_dependency,
                                subscription_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")

    subscription_model = db.query(Subscriptions).filter(
        Subscriptions.id == subscription_id).filter(
        Subscriptions.active == True).first()

    if subscription_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Subscription not found')

    active_subscription = db.query(UserSubscriptions).filter(
        UserSubscriptions.user_id == user.get('id')).filter(
        UserSubscriptions.expiry_date >= datetime.now()).first()

    if active_subscription is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='You already have an active subscription')

    user_subscription = UserSubscriptions(
        user_id=user.get('id'),
        subscription_id=subscription_model.id,
        requests_remaining=subscription_model.request_count,
        start_date=datetime.now(),
        expiry_date=datetime.now() + timedelta(days=subscription_model.duration_days),
    )

    db.add(user_subscription)

    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if user_model is not None:
        user_model.is_subscribed = True
        db.add(user_model)

    db.commit()
