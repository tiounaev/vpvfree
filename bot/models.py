from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Numeric,
    Boolean,
    func,
)
from sqlalchemy.orm import relationship
from bot.services.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)
    referral_code = Column(String(32), unique=True, nullable=False)
    referrer_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    referrals = relationship("User", backref="referrer", remote_side=[id], lazy="selectin")
    trials = relationship("Trial", back_populates="user", lazy="selectin")
    purchases = relationship("Purchase", back_populates="user", lazy="selectin")


class Trial(Base):
    __tablename__ = "trials"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    uuid = Column(String(64), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    user = relationship("User", back_populates="trials", lazy="joined")


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    uuid = Column(String(64), unique=True, index=True, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="purchases", lazy="joined")


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), unique=True, nullable=False)     # Пример: 🇺🇸 США
    code = Column(String(16), unique=True, nullable=False)     # Пример: us
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)                # ← Обязательно

    tariffs = relationship("Tariff", back_populates="location", lazy="selectin")


class Tariff(Base):
    __tablename__ = "tariffs"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    duration_days = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    title = Column(String(64), nullable=False)

    location = relationship("Location", back_populates="tariffs", lazy="joined")
