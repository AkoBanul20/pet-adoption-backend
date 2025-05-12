from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.database import get_db
# from app.core.auth import get_current_active_user
from app.models.user import User
from app.schemas.vaccination import (
    VaccinationCreate,
    VaccinationUpdate,
    VaccinationResponse,
    VaccinationListResponse
)
from app.crud.vaccination import (
    create_vaccination_record,
    get_vaccination_records,
    get_vaccination_record,
    update_vaccination_record,
    delete_vaccination_record
)

router = APIRouter()

@router.post(
    "/vaccinations",
    response_model=VaccinationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new vaccination record"
)
def create_vaccination(
    *,
    vaccination_in: VaccinationCreate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_active_user)
):
    """
    Create a new vaccination record with the following information:
    - **pet_id**: ID of the pet receiving vaccination
    - **vaccine_type**: Type of vaccine administered
    - **owner**: Name of pet owner
    - **contact**: Contact information
    - **administered_by**: Name of veterinarian or clinic
    - **expiration_date**: Vaccine expiration date
    - **notes**: Additional notes (optional)
    """
    return create_vaccination_record(db=db, vaccination_in=vaccination_in)

@router.get(
    "/vaccinations",
    response_model=VaccinationListResponse,
    summary="Get list of vaccination records"
)
def list_vaccinations(
    *,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    pet_id: Optional[int] = Query(None, description="Filter by pet ID"),
    vaccine_type: Optional[str] = Query(None, description="Filter by vaccine type")
):
    """
    Retrieve vaccination records with optional filtering and pagination:
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    - **pet_id**: Filter by specific pet (optional)
    - **vaccine_type**: Filter by vaccine type (optional)
    """
    return get_vaccination_records(
        db=db,
        skip=skip,
        limit=limit,
        pet_id=pet_id,
        vaccine_type=vaccine_type
    )

@router.get(
    "/vaccinations/{vaccination_id}",
    response_model=VaccinationResponse,
    summary="Get a specific vaccination record"
)
def get_vaccination(
    vaccination_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific vaccination record by its ID
    """
    return get_vaccination_record(db=db, record_id=vaccination_id)

@router.patch(
    "/vaccinations/{vaccination_id}",
    response_model=VaccinationResponse,
    summary="Update a vaccination record"
)
def update_vaccination(
    *,
    vaccination_id: int,
    vaccination_update: VaccinationUpdate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_active_user)
):
    """
    Update an existing vaccination record with the following fields (all optional):
    - **vaccine_type**: Type of vaccine administered
    - **owner**: Name of pet owner
    - **contact**: Contact information
    - **administered_by**: Name of veterinarian or clinic
    - **expiration_date**: Vaccine expiration date
    - **notes**: Additional notes
    """
    return update_vaccination_record(
        db=db,
        record_id=vaccination_id,
        vaccination_update=vaccination_update
    )

@router.delete(
    "/vaccinations/{vaccination_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a vaccination record"
)
def delete_vaccination(
    vaccination_id: int,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_active_user)
):
    """
    Soft delete a vaccination record
    """
    return delete_vaccination_record(db=db, record_id=vaccination_id)