from datetime import datetime
from typing import Any, List, Optional
from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session


from app.core.database import get_db
from app.api.deps import get_current_user
from app.crud.pet import (
    create_pet,
    update_pet,
    search_pets,
    get_pets,
    get_pet,
    get_pets_by_owner,
)
from app.schemas.pet import Pet, PetCreate, PetsByOwner
from app.models.user import User

router = APIRouter()


@router.post("/add", response_model=Pet, status_code=status.HTTP_201_CREATED)
def create_pet_route(
    *,
    db: Session = Depends(get_db),
    pet_in: PetCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create new pet record
    """
    created_pet = create_pet(db=db, pet_in=pet_in, current_user=current_user)
    return created_pet


@router.get("/list", response_model=List[Pet])
def read_pets_route(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 0,
    type: Optional[str] = None,
    gender: Optional[str] = None,
    breed: Optional[str] = None,
    color: Optional[str] = None,
    admin_featured: bool = False,
) -> Any:
    """
    Retrieve all pets record.
    """
    pets = get_pets(
        db=db,
        skip=skip,
        limit=limit,
        type=type,
        gender=gender,
        breed=breed,
        color=color,
        added_by_admin=admin_featured,
    )

    return pets


@router.get("/{pet_id}", response_model=Pet)
def read_pet_route(
    *,
    db: Session = Depends(get_db),
    pet_id: int,
) -> Any:
    """
    Get Pet record by id
    """
    pet = get_pet(
        db=db,
        pet_id=pet_id,
    )
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pet not found"
        )

    return pet


@router.get("/search/{search_term}", response_model=List[Pet])
def search_pets_route(
    *,
    search_term: str,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 0,
) -> Any:
    """
    Search for pets based on a search term in multiple fields
    """

    if not search_term:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="search term field is blank"
        )

    search_pets_result = search_pets(
        db=db,
        search_term=search_term,
        skip=skip,
        limit=limit,
    )

    return search_pets_result


@router.get("/list/mine", response_model=List[PetsByOwner])
def read_pets_by_owner_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get list of pet by Owner"""

    # print(current_user, "from routes")

    pets_by_owner = get_pets_by_owner(
        db=db,
        current_user=current_user,
    )

    return pets_by_owner
