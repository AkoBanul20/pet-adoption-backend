from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.models.transfer_coordinator import PetType
from .user import UserInDBBase

class TransferCoordinationBase(BaseModel):
    barangay_name: Optional[str] = Field(None, description="Name of the barangay")
    address: str = Field(..., description="Complete address for transfer")
    pet_type: PetType = Field(..., description="Type of pet (Dog or Cat)")
    request_datetime: datetime = Field(..., description="date of request")

class TransferCoordinationCreate(TransferCoordinationBase):
    pass

class TransferCoordinationUpdate(BaseModel):
    barangay_name: Optional[str] = None
    address: Optional[str] = None
    pet_type: Optional[PetType] = None

class TransferCoordinationInDBBase(TransferCoordinationBase):
    id: int
    user: Optional[UserInDBBase]
    status: str
    request_datetime: datetime
    

    class Config:
        from_attributes = True

class TransferCoordinationResponse(TransferCoordinationInDBBase):
    pass

class TransferCoordinationInDB(TransferCoordinationInDBBase):
    pass

class TransferCoordinationListResponse(BaseModel):
    items: List[TransferCoordinationResponse]
    total: int

class TransferCoordinationStatusUpdate(BaseModel):
    status: str = Field(
        ..., 
        description="Status of the transfer coordination request"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "status": "ACCEPTED"
            }
        }