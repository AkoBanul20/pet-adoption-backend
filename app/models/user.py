from sqlalchemy import Boolean, Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True, index=True)
    last_name = Column(String(255), nullable=True, index=True)
    middle_name = Column(String(255), nullable=True, index=True)
    contact = Column(String(25), nullable=True, index=True)
    home_street = Column(String(255), nullable=True)
    city = Column(String(255), nullable=True)
    region = Column(String(255),nullable=True)
    postal_code = Column(String(4), nullable=True)
    country = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    pets = relationship("Pet", back_populates="owner", cascade="all, delete-orphan")
    lost_pet_reports = relationship("LostPetReport", back_populates="reporter")
    transfer_coordinations = relationship(
        "TransferCoordination", 
        back_populates="user",
        cascade="all, delete-orphan"
    )