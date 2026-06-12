from typing import Annotated
from datetime import timedelta, datetime, timezone


from fastapi import APIRouter, status, HTTPException, Path, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2AuthorizationCodeBearer
from pydantic import BaseModel

from models import RoleTypes, Users
from .db import db_dependency

from passlib.context import CryptContext

from jose import jwt


SECRET_KEY = 'd10e488108e625064e04094c30fd643a5750b979eb26554074cca78d50b9d12b'
ALGORITHM = 'HS256'

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

bcrypt_content = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2AuthorizationCodeBearer(
    authorizationUrl='auth/token', tokenUrl='auth/token'
)


class CreateUserRequest(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str
    password: str
    is_active: bool
    is_subscribed: bool
    role: RoleTypes


class Token(BaseModel):
    access_token: str
    token_type: str


def authenticate_user(username: str, password: str, user: CreateUserRequest):
    if not user:
        return False
    if not bcrypt_content.verify(password, user.hashed_password):
        return False
    return True


def create_access_token(username: str, user_id: str, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.now(timezone.utc)

    encode.update({'exp': expires})

    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('user_id')

        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='could not validate user')
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='could not validate user')


@router.post("/create-user", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    user_model = Users(
        email=create_user_request.email,
        first_name=create_user_request.email,
        username=create_user_request.username,
        last_name=create_user_request.last_name,
        hashed_password=bcrypt_content.hash(create_user_request.password),
        is_subscribed=create_user_request.is_subscribed,
        is_active=create_user_request.is_active,
        role=create_user_request.role,
    )

    db.add(user_model)
    db.commit()


@router.put("/update-user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest, user_id: int = Path(gt=0)):
    update_user_model = db.query(Users).filter(Users.id == user_id).first()

    if update_user_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='user not found')

    update_user_model.email = create_user_request.email
    update_user_model.first_name = create_user_request.email
    update_user_model.username = create_user_request.username
    update_user_model.last_name = create_user_request.last_name
    update_user_model.hashed_password = bcrypt_content.hash(
        create_user_request.password)
    update_user_model.is_subscribed = create_user_request.is_subscribed
    update_user_model.is_active = create_user_request.is_active
    update_user_model.role = create_user_request.role

    db.add(update_user_model)
    db.commit()


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = db.query(Users).filter(Users.username == form_data.username).first()
    authenticated_user = authenticate_user(
        form_data.username, form_data.password, user)

    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='could not validate user')

    token = create_access_token(user.username, user.id, timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}
