import enum
from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Boolean, Numeric, Enum, ForeignKey, Date, DateTime
from database import Base
from sqlalchemy.orm import relationship


class OfferCategory(str, enum.Enum):
    DATA = "data"
    SMS = "sms"
    MINUTES = "minutes"


class RoleTypes(str, enum.Enum):
    CLIENT = "client"
    ADMIN = "admin"


class TransactionStatusTypes(str, enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"


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

    account = relationship("UserAccount", back_populates="user",
                           uselist=False, cascade="all, delete-orphan")


class Offers(Base):
    __tablename__ = 'offers'

    id = Column(Integer, primary_key=True, index=True)
    offer_name = Column(String(255), nullable=False)
    ussd = Column(String(50), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    category = Column(Enum(OfferCategory), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))


class Transactions(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'),
                     nullable=False, index=True)
    offer_id = Column(Integer, ForeignKey('offers.id'), nullable=False)
    customer_name = Column(String, nullable=False)
    customer_phone = Column(Integer, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(TransactionStatusTypes),
                    nullable=False, index=True)
    created_at = Column(Date, nullable=False)


class Subscriptions(Base):
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    request_count = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    duration_days = Column(Integer, nullable=False, default=30)
    active = Column(Boolean, default=True, nullable=False)


class UserSubscriptions(Base):
    __tablename__ = 'user_subscriptions'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'),
                     nullable=False, index=True)
    subscription_id = Column(Integer, ForeignKey(
        'subscriptions.id'), nullable=False)
    requests_remaining = Column(Integer, nullable=False)
    start_date = Column(DateTime, nullable=False, default=datetime.now)
    expiry_date = Column(DateTime, nullable=False, index=True)


class UserAccount(Base):
    __tablename__ = 'user_accounts'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'),
                     nullable=False, unique=True, index=True)
    balance = Column(Integer, default=0)
    modified_at = Column(Date, nullable=False, default=date.today)

    user = relationship("Users", back_populates="account", uselist=False)
