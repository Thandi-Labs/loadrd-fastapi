import enum
from sqlalchemy import Column, Integer, String, Boolean, Numeric, Enum
from database import Base


class OfferCategory(str, enum.Enum):
    DATA = "data"
    SMS = "sms"
    MINUTES = "minutes"


class Offers(Base):
    __tablename__ = 'offers'

    id = Column(Integer, primary_key=True, index=True)
    offer_name = Column(String(255), nullable=False)
    ussd = Column(String(50), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    category = Column(Enum(OfferCategory), nullable=False, index=True)
