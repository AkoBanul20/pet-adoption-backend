from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import Session, joinedload
from app.models.pet import Pet, LostPet
from app.schemas.lost_pet import LostPetCreate, LostPetUpdate


def create_lost_pet(
    db: Session,
    lost_pet_in: LostPetCreate,
    # pet_lost: Pet,
) -> LostPet:
    """Create a lost pet entry"""

    db_lost_pet = LostPet(
        pet_id=lost_pet_in.pet_id,
        last_seen_location=lost_pet_in.last_seen_location,
        last_seen_date=lost_pet_in.last_seen_date,
        additional_details=lost_pet_in.additional_details,
    )

    db.add(db_lost_pet)
    db.commit()
    db.refresh(db_lost_pet)

    return db_lost_pet


def get_lost_pets(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    status: Optional[str] = None,
    pet_type: Optional[str] = None,
    breed: Optional[str] = None,
    color: Optional[str] = None,
    size: Optional[str] = None,
    gender: Optional[str] = None,

) -> List[LostPet]:
    """
    Get all active lost pet reports with associated pet details.
    """
    query = db.query(LostPet)\
        .join(Pet, LostPet.pet_id == Pet.id)\
        .options(joinedload(LostPet.pet))\
        .filter(LostPet.deleted_at == None)
    
    # Apply filters if provided
    if pet_type:
        query = query.filter(Pet.type == pet_type)
    if breed:
        query = query.filter(Pet.breed == breed)
    if color:
        query = query.filter(Pet.color == color)
    if size:
        query = query.filter(Pet.size == size)
    if gender:
        query = query.filter(Pet.gender == gender)
    if status:
        query = query.filter(LostPet.status == status)

    query = query.offset(skip).limit(limit).all()

    return query