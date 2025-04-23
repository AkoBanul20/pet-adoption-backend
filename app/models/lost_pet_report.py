from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    DateTime,
    func, 
    Text, 
    ForeignKey,
)

from sqlalchemy.orm import relationship
from app.core.database import Base



class LostPetReport(Base):
    __tablename__ = "lost_pet_reports"

    id = Column(Integer, primary_key=True, index=True)
    lost_pet_id = Column(Integer, ForeignKey("lost_pets.id", ondelete="CASCADE"), nullable=False, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    details = Column(Text, nullable=False)
    report_location = Column(String(255), nullable=False)
    report_date = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    image_url = Column(String(255), nullable=True, default=None)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), index=True)
    deleted_at = Column(DateTime, nullable=True, index=True)

    lost_pet  = relationship("LostPet", back_populates="reports")
    reporter = relationship("User", back_populates="lost_pet_reports")