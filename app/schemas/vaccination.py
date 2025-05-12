from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.vaccination import VaccineType
from app.schemas.pet import PetInDBBase

class VaccinationBase(BaseModel):
    pet_id: int = Field(..., description="ID of the pet receiving vaccination")
    vaccine_type: VaccineType = Field(..., description="Type of vaccine administered")
    owner: str = Field(..., description="Name of pet owner")
    contact: str = Field(..., description="Contact information")
    administered_by: str = Field(..., description="Name of veterinarian or clinic")
    expiration_date: datetime = Field(..., description="Vaccine expiration date")
    notes: Optional[str] = Field(None, description="Additional notes")

class VaccinationCreate(VaccinationBase):
    pass

class VaccinationUpdate(BaseModel):
    vaccine_type: Optional[VaccineType] = Field(None, description="Type of vaccine administered")
    owner: Optional[str] = Field(None, description="Name of pet owner")
    contact: Optional[str] = Field(None, description="Contact information")
    administered_by: Optional[str] = Field(None, description="Name of veterinarian or clinic")
    expiration_date: Optional[datetime] = Field(None, description="Vaccine expiration date")
    notes: Optional[str] = Field(None, description="Additional notes")

class VaccinationInDBBase(VaccinationBase):
    id: int
    pet: Optional[PetInDBBase] = None
    administered_date: datetime
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class VaccinationResponse(VaccinationInDBBase):
    pass

class VaccinationInDB(VaccinationInDBBase):
    pass

class VaccinationListResponse(BaseModel):
    items: List[VaccinationResponse]
    total: int