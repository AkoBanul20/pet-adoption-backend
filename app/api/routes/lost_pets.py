from typing import Any, List, Optional
from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.lost_pet import create_lost_pet, get_lost_pets
from app.schemas.lost_pet import LostPet, LostPetCreate, LostPetDetailsResponse

# from app.models.pet import Pet


router = APIRouter()


@router.post("/add", response_model=LostPet, status_code=status.HTTP_201_CREATED)
def create_lost_pet_route(
    *,
    db: Session = Depends(get_db),
    lost_pet_in: LostPetCreate,
    # pet_to_report_lost: Pet,
) -> Any:
    """Create lost pet info"""

    created_lost_pet = create_lost_pet(db=db, lost_pet_in=lost_pet_in)

    return created_lost_pet


@router.get("/list", response_model=List[LostPetDetailsResponse])
def read_lost_pets_route(
    db: Session = Depends(get_db),
    skip=0, 
    limit=0,
) -> Any:
    """
    Retrieve all lost pets records.
    """

    lost_pets = get_lost_pets(db=db,skip=skip, limit=limit)

    return lost_pets