from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator

from app.models.pet import PetGender
from .user import UserInDBBase


class PetBase(BaseModel):
    type: str
    name: Optional[str] = None
    breed: Optional[str] = None
    age: Optional[str] = None
    color: str
    size: str
    description: str
    gender: str
    image_url: Optional[str] = None
    # owner_id: Optional[int] = None 
    # is_deleted: Optional[bool] = False

    class Config:
        from_attributes = True


class PetCreate(PetBase):
    gender: PetGender = PetGender.MALE

    @validator("type")
    def type_not_empty(cls, v: str):
        if not v or not v.strip():
            raise ValueError("Type cannot be empty..")
        return v.strip()

    @validator("color")
    def color_not_empty(cls, v: str):
        if not v or not v.strip():
            raise ValueError("Color cannot be empty..")
        return v.strip()

    @validator("size")
    def size_not_empty(cls, v: str):
        if not v or not v.strip():
            raise ValueError("Size cannot be empty..")
        return v.strip()

    @validator("description")
    def description_not_empty(cls, v: str):
        if not v or not v.strip():
            raise ValueError("Description cannot be empty..")
        return v.strip()


class UserDetailsResponse(UserInDBBase):
    pass

class PetUpdate(BaseModel):
    type: Optional[str] = None
    name: Optional[str] = None
    breed: Optional[str] = None
    gender: Optional[PetGender] = None
    age: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None


class PetInDBBase(PetBase):
    id: int
    owner: UserDetailsResponse
    # is_deleted: Optional[bool] = False
    # created_at: datetime
    # updated_at: Optional[datetime] = None

    class Config:
        # orm_mode = True
        from_attributes = True


class Pet(PetInDBBase):
    pass


class PetInDB(PetInDBBase):
    pass


class PetsByOwner(PetBase):
    id: int
    name: str

    class Config:
        from_attributes = True