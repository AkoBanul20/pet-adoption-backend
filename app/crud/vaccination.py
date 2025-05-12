from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException, status

from app.models.vaccination import VaccinationRecord, VaccineType
from app.models.pet import Pet
from app.schemas.vaccination import VaccinationCreate, VaccinationUpdate, VaccinationInDB

def create_vaccination_record(
    db: Session,
    vaccination_in: VaccinationCreate,
    # current_user: User
) -> VaccinationRecord:
    """Create a new vaccination record"""
    try:
        # Verify pet exists
        pet = db.query(Pet).filter(Pet.id == vaccination_in.pet_id).first()
        if not pet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pet with ID {vaccination_in.pet_id} not found"
            )

        # Validate vaccine type
        try:
            vaccine_type = VaccineType(vaccination_in.vaccine_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid vaccine type. Must be one of: {', '.join([v.value for v in VaccineType])}"
            )

        # Create vaccination record
        db_vaccination = VaccinationRecord(
            pet_id=vaccination_in.pet_id,
            vaccine_type=vaccine_type,
            owner=vaccination_in.owner,
            contact=vaccination_in.contact,
            administered_by=vaccination_in.administered_by,
            expiration_date=vaccination_in.expiration_date,
            notes=vaccination_in.notes
        )

        db.add(db_vaccination)
        db.commit()
        db.refresh(db_vaccination)

        return VaccinationInDB.model_validate(db_vaccination)

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database integrity error: {str(e)}"
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

def get_vaccination_records(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    pet_id: Optional[int] = None,
    vaccine_type: Optional[str] = None
):
    """Get list of vaccination records with optional filters"""
    try:
        # Base query
        query = db.query(VaccinationRecord).filter(VaccinationRecord.deleted_at.is_(None))

        # Apply filters
        if pet_id:
            query = query.filter(VaccinationRecord.pet_id == pet_id)

        if vaccine_type:
            try:
                validated_type = VaccineType(vaccine_type)
                query = query.filter(VaccinationRecord.vaccine_type == validated_type)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid vaccine type. Must be one of: {', '.join([v.value for v in VaccineType])}"
                )

        # Get total count
        total = query.count()

        # Apply pagination and load relationships
        records = (
            query
            .options(joinedload(VaccinationRecord.pet))
            .order_by(VaccinationRecord.administered_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return {"items": records, "total": total}

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

def get_vaccination_record(
    db: Session,
    record_id: int
) -> VaccinationRecord:
    """Get a specific vaccination record by ID"""
    try:
        record = (
            db.query(VaccinationRecord)
            .filter(
                VaccinationRecord.id == record_id,
                VaccinationRecord.deleted_at.is_(None)
            )
            .first()
        )

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vaccination record with ID {record_id} not found"
            )

        return VaccinationInDB.model_validate(record)

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

def update_vaccination_record(
    db: Session,
    record_id: int,
    vaccination_update: VaccinationUpdate
) -> VaccinationRecord:
    """Update an existing vaccination record"""
    try:
        record = (
            db.query(VaccinationRecord)
            .filter(
                VaccinationRecord.id == record_id,
                VaccinationRecord.deleted_at.is_(None)
            )
            .first()
        )

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vaccination record with ID {record_id} not found"
            )

        # Update fields
        update_data = vaccination_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(record, field, value)

        db.commit()
        db.refresh(record)

        return VaccinationInDB.model_validate(record)

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database integrity error: {str(e)}"
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

def delete_vaccination_record(
    db: Session,
    record_id: int
):
    """Soft delete a vaccination record"""
    try:
        record = (
            db.query(VaccinationRecord)
            .filter(
                VaccinationRecord.id == record_id,
                VaccinationRecord.deleted_at.is_(None)
            )
            .first()
        )

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vaccination record with ID {record_id} not found"
            )

        # Soft delete
        record.deleted_at = datetime.utcnow()
        db.commit()

        return {"message": "Vaccination record deleted successfully"}

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )