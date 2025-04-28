import enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    func,
    Text,
    Enum,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class PetGender(str, enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"


class Pet(Base):
    __tablename__ = "pets"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)
    breed = Column(String(100), nullable=True)
    gender = Column(Enum(PetGender), default=PetGender.MALE)
    age = Column(String(50), nullable=True)
    color = Column(String(100), nullable=False)
    size = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    image_url = Column(String(255), nullable=True, default=None)  # for image upload
    # is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True, onupdate=func.now())
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    owner_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Relationship for users
    owner = relationship("User", back_populates="pets")

    # New relationship for lost pet report
    lost_pet = relationship(
        "LostPet", back_populates="pet", uselist=False, cascade="all, delete-orphan"
    )

    # New relationship for adoption pets
    adoption_pet = relationship(
        "AdoptionPet", back_populates="pet", uselist=False, cascade="all, delete-orphan"
    )


class LostPetStatus(str, enum.Enum):
    REPORTED = "REPORTED"
    SEARCHING = "SEARCHING"
    FOUND = "FOUND"
    RESOLVED = "REUNITED"


class LostPet(Base):
    __tablename__ = "lost_pets"

    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id", ondelete="CASCADE"), nullable=False)
    last_seen_location = Column(String(255), nullable=False)
    last_seen_date = Column(DateTime, nullable=False)
    additional_details = Column(Text, nullable=True)
    status = Column(Enum(LostPetStatus), nullable=False, default=LostPetStatus.REPORTED)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True, onupdate=func.now())

    pet = relationship("Pet", back_populates="lost_pet")
    reports = relationship(
        "LostPetReport", back_populates="lost_pet", cascade="all, delete-orphan"
    )


class AdoptionPet(Base):
    __tablename__ = "adoption_pets"

    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(
        Integer, ForeignKey("pets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    found_in = Column(String(255), nullable=False)
    additional_details = Column(Text, nullable=True)
    media = Column(JSON, nullable=True)
    status = Column(
        String(50),
        default="AVAILABLE",
        nullable=False,
        index=True,
    )  # available, adopted, etc.
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), index=True
    )
    deleted_at = Column(DateTime, nullable=True, index=True)

    pet = relationship("Pet", back_populates="adoption_pet")
