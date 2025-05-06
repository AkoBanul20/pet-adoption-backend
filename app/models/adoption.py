import enum
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    func,
    Text,
    ForeignKey,
    Boolean,
)

from sqlalchemy.orm import relationship
from app.core.database import Base

#TOD0: create table then make a route and logic
class Adoption(Base):
    __tablename__ = 'adoptions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    adoption_pet_id = Column(Integer, ForeignKey('adoption_pets.id'), nullable=False)
    adopter_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)  # or 'adopters.id'
    adoption_date = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False, default='pending')  # e.g., pending, approved, rejected
    notes = Column(Text)
    approved_by = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)  # admin who approved
    agreement_signed = Column(Boolean, default=False)
    schedule = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), index=True)
    deleted_at = Column(DateTime, nullable=True, index=True)


    # Relationships (optional, for easier ORM access)
    adoption_pet = relationship('AdoptionPet', back_populates='adoptions')
    adopter = relationship('User', foreign_keys=[adopter_id])
    approved_admin = relationship('User', foreign_keys=[approved_by])