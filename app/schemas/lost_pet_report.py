from typing import Optional
from datetime import datetime

from pydantic import BaseModel, validator
from .lost_pet import LostPetInDBBase
from .user import UserInDBBase


class LostPetReportBase(BaseModel):
    lost_pet_id: int
    reporter_id: int
    details: str
    report_location: str


class LostPetReportCreate(LostPetReportBase):
    @validator("details")
    def details_not_empty(cls, v: str):
        if not v or not v.strip():
            raise ValueError("Details cannot be empty..")
        return v.strip()

    @validator("report_location")
    def report_location_not_empty(cls, v: str):
        if not v or not v.strip():
            raise ValueError("Report location cannot be empty..")
        return v.strip()
    

class LostPetReportUpdate(BaseModel):
    details: Optional[str] = None
    report_location: Optional[str] = None

    @validator("details")
    def details_not_empty(cls, v: str):
        if not v or not v.strip():
            raise ValueError("Details cannot be empty..")
        return v.strip()

    @validator("report_location")
    def report_location_not_empty(cls, v: str):
        if not v or not v.strip():
            raise ValueError("Report location cannot be empty..")
        return v.strip()

class LostPetReportInDBBase(LostPetReportBase):
    id: int
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class LostPetReport(LostPetReportInDBBase):
    pass

class LostPetReportInDB(LostPetReportInDBBase):
    pass


class ReporterBasicInfo(BaseModel):
    full_name: str

    class Config:
        from_attributes = True


class LostPetReportDetailsResponse(BaseModel):
    id: int
    lost_pet: LostPetInDBBase
    details: str
    reporter: ReporterBasicInfo
    report_location: str
    report_date: datetime
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    

    class Config:
        from_attributes = True