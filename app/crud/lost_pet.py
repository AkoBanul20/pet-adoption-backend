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
) -> List[LostPet]:
    """
    Get all active lost pet reports with associated pet details.
    """
    _query = db.query(LostPet)\
        .options(joinedload(LostPet.pet))\
        .filter(LostPet.deleted_at == None)

    query = _query.offset(skip).limit(limit).all()

    return query