from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import Session
from app.models.pet import Pet
from app.models.user import User
from app.schemas.pet import PetCreate, PetUpdate


def get_pet(db: Session, pet_id: int) -> Optional[Pet]:
    """Get a specific pet by ID"""
    return db.query(Pet).filter(Pet.id == pet_id).first()


def get_pets(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    type: Optional[str] = None,
    gender: Optional[str] = None,
    breed: Optional[str] = None,
    color: Optional[str] = None,
    size: Optional[str] = None,
    added_by_admin: Optional[bool] = None,
) -> List[Pet]:
    """
    Get multiple pets with optional filtering
    """
    query = db.query(Pet).join(User, Pet.owner_id == User.id)

    if added_by_admin:
        query = query.filter(User.is_superuser == True)

    # Apply filters if provided
    if type:
        query = query.filter(Pet.type == type)
    if gender:
        query = query.filter(Pet.gender == gender)
    if breed:
        query = query.filter(Pet.breed == breed)
    if color:
        query = query.filter(Pet.color == color)
    if size:
        query = query.filter(Pet.size == size)

    return query.offset(skip).limit(limit).all()


def create_pet(
    db: Session,
    pet_in: PetCreate,
    current_user: User,
) -> Pet:
    """Create a new pet entry"""

    db_pet = Pet(
        type=pet_in.type,
        name=pet_in.name,
        breed=pet_in.breed,
        gender=pet_in.gender,
        age=pet_in.age,
        color=pet_in.color,
        size=pet_in.size,
        description=pet_in.description,
        owner_id=current_user.id,
    )
    db.add(db_pet)
    db.commit()
    db.refresh(db_pet)

    return db_pet


def update_pet(
    db: Session,
    *,
    db_pet: Pet,
    pet_in: Union[PetUpdate, Dict[str, Any]],
) -> Pet:
    """Update an existing pet"""

    if isinstance(pet_in, dict):
        update_data = pet_in
    else:
        update_data = pet_in.model_dump(exclude_unset=True)

    for field in update_data:
        if update_data[field] is not None:
            setattr(db_pet, field, update_data[field])

    db.add(db_pet)
    db.commit()
    db.refresh(db_pet)

    return db_pet


def delete_pet(
    db: Session,
    *,
    pet_id: int,
) -> Pet:
    """Delete a pet"""

    pet = db.query(Pet).get(pet_id)
    if pet:
        db.delete(pet)
        db.commit()
    return pet


def search_pets(
    db: Session, search_term: str, skip: int = 0, limit: int = 100
) -> List[Pet]:
    """
    Search for pets based on a search term in multiple fields
    """
    search_pattern = f"%{search_term}%"
    return (
        db.query(Pet)
        .filter(
            Pet.description.ilike(search_pattern)
            | Pet.type.ilike(search_pattern)
            | Pet.breed.ilike(search_pattern)
            | Pet.name.ilike(search_pattern)
            | Pet.color.ilike(search_pattern)
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_pets_by_owner(db: Session, current_user: User) -> List[Pet]:
    """Get list of pets by Owner/User"""
    print(current_user, "this is from current user")
    query = db.query(Pet).filter(Pet.owner_id == int(current_user.id))

    return query.all()
