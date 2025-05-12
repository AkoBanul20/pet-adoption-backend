from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Text, func, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum

class VaccineType(str, enum.Enum):
    """Common pet vaccinations by type."""
    # Dog vaccines
    RABIES = "Rabies"
    DISTEMPER = "Distemper"
    PARVOVIRUS = "Parvovirus"
    ADENOVIRUS = "Adenovirus"
    BORDETELLA = "Bordetella"
    LEPTOSPIROSIS = "Leptospirosis"
    LYME = "Lyme Disease"
    
    # Cat vaccines
    FELINE_RABIES = "Feline Rabies"
    FELINE_DISTEMPER = "Feline Distemper (Panleukopenia)"
    FELINE_CALICIVIRUS = "Feline Calicivirus"
    FELINE_HERPESVIRUS = "Feline Herpesvirus"
    FELINE_LEUKEMIA = "Feline Leukemia"
    
    # Other
    OTHER = "Other"


class VaccinationRecord(Base):
    """SQLAlchemy model for completed vaccination records."""
    __tablename__ = "vaccination_records"
    
    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    vaccine_type = Column(Enum(VaccineType), nullable=False)
    owner = Column(String(36), nullable=False, index=True)
    contact = Column(String(100), nullable=False, index=True)
    administered_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    # vaccine_lot = Column(String(50), nullable=False)
    administered_by = Column(String(100), nullable=False)
    expiration_date = Column(DateTime, nullable=False)
    notes = Column(Text)
    deleted_at = Column(DateTime, nullable=True, onupdate=func.now())
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # relationships
    pet = relationship("Pet", back_populates="vaccination_records")