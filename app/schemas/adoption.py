from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

from .adoption_pet import AdoptionPetResponse
from .user import UserInDBBase


# Create/Add Schema
class AdoptionCreate(BaseModel):
    adoption_pet_id: int = Field(..., description="The ID of the pet being adopted")
    # adopter_id: int = Field(..., description="The ID of the adopter")
    notes: Optional[str] = Field(None, description="Additional notes about the adoption")


# Update Status Schema
class AdoptionStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    screening = "screening"

class AdoptionUpdateStatus(BaseModel):
    status: AdoptionStatus = Field(..., description="The status of the adoption (pending, approved, rejected)")
    schedule: Optional[datetime] = None
    approved_by: Optional[int] = None
    agreement_signed: Optional[bool] = None
    adoption_date: Optional[datetime] = None 



# Read/List Schema
class AdoptionRead(BaseModel):
    id: int
    adoption_pet: AdoptionPetResponse
    adopter: Optional[UserInDBBase]
    adoption_date: Optional[datetime]
    status: str
    notes: Optional[str]
    approved_admin: Optional[UserInDBBase]
    agreement_signed: bool
    schedule: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Enables compatibility with SQLAlchemy models




class AdoptionInDBBase(AdoptionRead):
    pass

class AdoptionInDB(AdoptionInDBBase):
    pass

class AdoptionListResponse(BaseModel):
    items: List[AdoptionRead]
    total: int

class AdoptionDocumentGeneration(BaseModel):
    adoption_id: int