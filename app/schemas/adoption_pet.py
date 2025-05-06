from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, validator, StrictBool

from .pet import PetInDBBase


class AdoptionPetBase(BaseModel):
    found_in: str
    is_vaccinated: StrictBool
    is_neutered: StrictBool
    additional_details: Optional[str] = None
    media: Optional[List] = None
    # status: str


class AdoptionPetCreate(AdoptionPetBase):
    pet_id: int

    @validator("found_in")
    def found_in_not_empty(cls, v: str):
        if not v or not v.strip():
            raise ValueError("found_in cannot be empty...")
        return v.strip()

    # @validator("status")
    # def last_seen_location_not_empty(cls, v: str):
    #     if not v or not v.strip():
    #         raise ValueError("last seen location cannot be empty...")
    #     return v.strip()


class AdoptionPetUpdateStatus(BaseModel):
    id: int
    status: str


class AdoptionPetUpdate(BaseModel):
    id: int
    found_in: Optional[str] = None
    is_vaccinated: Optional[bool] = None
    is_neutered: Optional[bool] = None
    additional_details: Optional[str] = None
    media: Optional[List[str]] = None


class AdoptionPetInDBBase(AdoptionPetBase):
    id: int
    pet: PetInDBBase
    status: str
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AdoptionPet(AdoptionPetInDBBase):
    pass


class AdoptionPetInDB(AdoptionPetInDBBase):
    pass


class AdoptionPetResponse(BaseModel):
    id: int
    found_in: str
    is_vaccinated: StrictBool
    is_neutered: StrictBool
    additional_details: Optional[str] = None
    media: Optional[List] = None
    status: str
    pet: PetInDBBase

    class Config:
        from_attributes = True
