from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator

from app.models.pet import LostPetStatus
from .pet import PetBase, PetInDBBase


class LostPetBase(BaseModel):
    pet_id: int
    last_seen_location: str
    last_seen_date: datetime
    additional_details: Optional[str] = None


class LostPetCreate(LostPetBase):
    status: LostPetStatus = LostPetStatus.REPORTED

    @validator("last_seen_location")
    def last_seen_location_not_empty(cls, v: str):
        if not v or not v.strip():
            raise ValueError("last seen location cannot be empty...")
        return v.strip()

    @validator("last_seen_date")
    def last_seen_date_not_empty(cls, v: datetime):
        if not v or not v.tzinfo:
            raise ValueError("Last seen date cannot be empty...")

        return v


class LostPetUpdate(BaseModel):
    status: Optional[LostPetStatus] = None
    last_seen_location: Optional[str] = None
    last_seen_date: Optional[datetime] = None
    additional_details: Optional[str] = None


class LostPetInDBBase(LostPetBase):
    id: int
    pet_id: int
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LostPet(LostPetInDBBase):
    pass


class LostPetInDB(LostPetInDBBase):
    pass


class LostPetDetailsResponse(BaseModel):
    id: int
    last_seen_location: str
    last_seen_date: datetime
    additional_details: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    pet: PetInDBBase

    class Config:
        from_attributes = True