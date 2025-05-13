from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError


from app.models.lost_pet_report import LostPetReport
from app.models.pet import LostPet

from app.schemas.lost_pet_report import LostPetReportCreate, LostPetReportMatchUpdate

def create_lost_pet_report(db: Session, lost_pet_report_in: LostPetReportCreate) -> LostPetReport:
    """
    Create a new lost pet report.
    """
    db_lost_pet_report = LostPetReport(
        lost_pet_id=lost_pet_report_in.lost_pet_id,
        reporter_id=lost_pet_report_in.reporter_id,
        details=lost_pet_report_in.details,
        report_location=lost_pet_report_in.report_location,
        image_url=lost_pet_report_in.image_url,
        
    )

    db.add(db_lost_pet_report)
    db.commit()
    db.refresh(db_lost_pet_report)

    return db_lost_pet_report


def get_lost_pet_reports(
    db: Session,
    skip: int = 0,
    limit: int = 10,
) -> List[LostPetReport]:
    """
    Get all lost pet reports.
    """
    query = db.query(LostPetReport)\
        .join(LostPet, LostPetReport.lost_pet_id == LostPet.id)\
        .options(joinedload(LostPetReport.lost_pet))\
        .filter(LostPetReport.is_matched == True)\
        .filter(LostPetReport.deleted_at == None)
    

    return query.offset(skip).limit(limit).all()


def get_lost_pet_report_by_id(
    db: Session,
    lost_pet_report_id: int,
) -> LostPetReport:
    """
    Get a lost pet report by its ID.
    """
    return db.query(LostPetReport).filter(LostPetReport.id == lost_pet_report_id).first()


def update_lost_pet_report_match(
    db: Session,
    report_id: int,
    match_update: LostPetReportMatchUpdate
) -> LostPetReport:
    """Update the is_matched status of a lost pet report"""
    try:
        report = db.query(LostPetReport).filter(
            LostPetReport.id == report_id,
            LostPetReport.deleted_at.is_(None)
        ).first()

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lost pet report with ID {report_id} not found"
            )

        report.is_matched = match_update.is_matched
        db.commit()
        db.refresh(report)

        return report

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )