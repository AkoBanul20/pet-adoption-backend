from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum
from datetime import datetime

class PetType(str, enum.Enum):
    DOG = "Dog"
    CAT = "Cat"



class TransferCoordination(Base):
    __tablename__ = "transfer_coordinations"

    id = Column(Integer, primary_key=True, index=True)
    barangay_name = Column(String(255), index=True, nullable=True)
    address = Column(Text)
    request_datetime = Column(DateTime, nullable=True, index=True, default=datetime.utcnow)
    pet_type = Column(Enum(PetType), nullable=False)
    status = Column(String(255), index=True, nullable=True, default="PENDING")
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True, onupdate=func.now())
    

    # Relationships
    user = relationship("User", back_populates="transfer_coordinations")