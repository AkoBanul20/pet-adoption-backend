from typing import List, Optional


from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException, status


from app.models.adoption import Adoption
from app.models.pet import AdoptionPet
from app.models.user import User
from app.schemas.adoption import (
    AdoptionCreate,
    AdoptionUpdateStatus,
    AdoptionInDB,
    AdoptionStatus
)

def create_adoption_request(db:Session,adoption_in: AdoptionCreate, current_user: User)-> Adoption:
    try:
        adoption_pet = db.query(AdoptionPet).filter(AdoptionPet.id == adoption_in.adoption_pet_id).first()
        if not adoption_pet:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pet with ID {adoption_in.adoption_pet_id} not found",
        )

        db_adoption = Adoption(
            adoption_pet_id = adoption_in.adoption_pet_id,
            adopter_id = current_user.id,
            notes = adoption_in.notes
        )

        db.add(db_adoption)
        db.commit()
        db.refresh(db_adoption)

        return AdoptionInDB.model_validate(db_adoption)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database integrity error: {str(e)}",
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )


def get_adoption_list(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    status: Optional[List[str]] = None,
):
    """
    Get list of adoptions
    """
    try:
        base_query = db.query(Adoption)

        if status:
            validated_statuses = []
            for s in status:
                try:
                    validated_status = AdoptionStatus(s)
                    validated_statuses.append(validated_status)
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid status: {s}. Must be one of: {', '.join([s.value for s in AdoptionStatus])}",
                    )
           
            base_query = base_query.filter(Adoption.status.in_(validated_statuses))

        total = base_query.count()
        adoptions = (
            db.query(Adoption)
            .join(AdoptionPet, Adoption.adoption_pet_id == AdoptionPet.id)
            .options(joinedload(Adoption.adoption_pet))
        )

        if status:
            adoptions = adoptions.filter(Adoption.status.in_(validated_statuses))

        return {"items": adoptions.offset(skip).limit(limit).all(), "total": total}

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database integrity error: {str(e)}",
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )


def update_adoption_request_status(
        db: Session,
        adoption_id:int,
        adoption_status_in: AdoptionUpdateStatus
):  
    try:
        update_adoption_status = db.query(Adoption).filter(Adoption.id == adoption_id).first()

        if not update_adoption_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Adoption request  with ID {adoption_id} not found",
            )

        if adoption_status_in.status == "screening":
            update_adoption_status.schedule = adoption_status_in.schedule

        if adoption_status_in.status == "approved":
            update_adoption_status.approved_by = adoption_status_in.approved_by
            update_adoption_status.adoption_date = adoption_status_in.adoption_date
            update_adoption_status.agreement_signed = adoption_status_in.agreement_signed


        update_adoption_status.status = adoption_status_in.status

        db.commit()
        db.refresh(update_adoption_status)

        return AdoptionInDB.model_validate(update_adoption_status)

    except IntegrityError as e:
        # Roll back the transaction in case of constraint violations
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database integrity error: {str(e)}",
        )
    except SQLAlchemyError as e:
        # Roll back the transaction in case of any other database errors
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )