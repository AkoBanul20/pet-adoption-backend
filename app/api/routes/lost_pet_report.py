from typing import Any, List, Optional
from fastapi import APIRouter,Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.lost_pet_report import create_lost_pet_report, get_lost_pet_reports, get_lost_pet_report_by_id
from app.schemas.lost_pet_report import LostPetReport, LostPetReportCreate, LostPetReportDetailsResponse



router = APIRouter()


@router.post("/add", response_model=LostPetReport, status_code=status.HTTP_201_CREATED)
def create_lost_pet_report_route(
    *,
    db: Session = Depends(get_db),
    lost_pet_report_in: LostPetReportCreate,
) -> Any:
    """Create lost pet report"""

    created_lost_pet_report = create_lost_pet_report(db=db, lost_pet_report_in=lost_pet_report_in,)

    return created_lost_pet_report


@router.get("/list", response_model=List[LostPetReportDetailsResponse], status_code=status.HTTP_200_OK)
def read_lost_pet_reports_route(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 0,
) -> Any:
    """
    Retrieve all lost pet reports.
    """

    lost_pet_reports = get_lost_pet_reports(db=db, skip=skip, limit=limit)

    return lost_pet_reports


@router.get("/{report_id}", response_model=LostPetReportDetailsResponse, status_code=status.HTTP_200_OK)
def read_lost_pet_report_route(
    *,
    db: Session = Depends(get_db),
    report_id: int,
) -> Any:
    """
    Retrieve a specific lost pet report by ID.
    """

    lost_pet_report = get_lost_pet_report_by_id(db=db, lost_pet_report_id=report_id)

    if not lost_pet_report:
        raise HTTPException(status_code=404, detail="Lost pet report not found")

    return lost_pet_report