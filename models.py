import enum
from sqlalchemy import Column, Integer, String, Boolean, Numeric, Enum, ForeignKey
from database import Base


class OfferCategory(str, enum.Enum):
    DATA = "data"
    SMS = "sms"
    MINUTES = "minutes"


class RoleTypes(str, enum.Enum):
    CLIENT = "client"
    ADMIN = "admin"


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_subscribed = Column(Boolean, default=True)
    role = Column(Enum(RoleTypes), nullable=False, index=True)


class Offers(Base):
    __tablename__ = 'offers'

    id = Column(Integer, primary_key=True, index=True)
    offer_name = Column(String(255), nullable=False)
    ussd = Column(String(50), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    category = Column(Enum(OfferCategory), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
