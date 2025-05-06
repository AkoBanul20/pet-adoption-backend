from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.adoption_pet import (
    AdoptionPetCreate,
    AdoptionPetInDB,
    AdoptionPetResponse,
    AdoptionPetUpdate,
    AdoptionPetUpdateStatus,
)

from app.crud.adoption_pet import (
    create_for_adoption_pet,
    update_adoption_pet,
    update_pet_status,
    get_pets_available,
    get_adoption_pet_details,
)

router = APIRouter()


@router.post(
    "/add", response_model=AdoptionPetResponse, status_code=status.HTTP_201_CREATED
)
def create_adoption_pet_route(
    adoption_pet_in: AdoptionPetCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new pet for adoption.
    """
    return create_for_adoption_pet(db=db, adoption_pet_in=adoption_pet_in)


@router.get(
    "/list-available",
    response_model=List[AdoptionPetResponse],
    status_code=status.HTTP_200_OK,
)
def read_adoption_pets_route(
    skip: int = 0,
    limit: int = 10,
    pet_type: Optional[str] = None,
    breed: Optional[str] = None,
    color: Optional[str] = None,
    size: Optional[str] = None,
    gender: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Retrieve all pets available for adoption with optional filtering.

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **pet_type**: Filter by pet type (e.g., 'dog', 'cat')
    - **breed**: Filter by breed
    - **color**: Filter by color
    - **size**: Filter by size
    - **gender**: Filter by gender
    """
    adoption_pets = get_pets_available(
        db=db,
        skip=skip,
        limit=limit,
        pet_type=pet_type,
        breed=breed,
        color=color,
        size=size,
        gender=gender,
    )
    return adoption_pets

@router.get("/{adoption_pet_id}", response_model=AdoptionPetResponse)
def read_adoption_pet(
    adoption_pet_id: int,
    db: Session = Depends(get_db),
):
    """
    Get a specific pet for adoption by ID.
    """
    adoption_pet = get_adoption_pet_details(db=db, pet_id=adoption_pet_id)
    if adoption_pet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Adoption pet with ID {adoption_pet_id} not found"
        )
    return adoption_pet


@router.put("/update", response_model=AdoptionPetResponse)
def update_adoption_pet_details_route(
    adoption_pet_update: AdoptionPetUpdate,
    db: Session = Depends(get_db),
):
    """
    Update details of a pet for adoption.
    """
    return update_adoption_pet(db=db, pet_update=adoption_pet_update)


@router.patch("/status/", response_model=AdoptionPetResponse)
def update_adoption_pet_status_route(
    status_update: AdoptionPetUpdateStatus,
    db: Session = Depends(get_db),
):
    """
    Update the adoption status of a pet.
    """
    return update_pet_status(db=db, status_update=status_update)
