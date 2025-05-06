from typing import Any, List, Optional


from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException, status


from app.models.pet import Pet, AdoptionPet
from app.schemas.adoption_pet import (
    AdoptionPetCreate,
    AdoptionPetUpdateStatus,
    AdoptionPetUpdate,
    AdoptionPetInDB,
)


def create_for_adoption_pet(
    db: Session,
    adoption_pet_in: AdoptionPetCreate,
) -> AdoptionPet:
    """Add pet for adoption"""

    pet = db.query(Pet).filter(Pet.id == adoption_pet_in.pet_id).first()
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pet with ID {adoption_pet_in.pet_id} not found",
        )

    try:

        db_adoption_pet = AdoptionPet(
            pet_id=adoption_pet_in.pet_id,
            found_in=adoption_pet_in.found_in,
            is_vaccinated=adoption_pet_in.is_vaccinated,
            is_neutered=adoption_pet_in.is_neutered,
            additional_details=adoption_pet_in.additional_details,
            media=adoption_pet_in.media,
        )

        db.add(db_adoption_pet)
        db.commit()
        db.refresh(db_adoption_pet)

        # return db_adoption_pet
        return AdoptionPetInDB.model_validate(db_adoption_pet)

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


def get_pets_available(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    pet_type: Optional[str] = None,
    breed: Optional[str] = None,
    color: Optional[str] = None,
    size: Optional[str] = None,
    gender: Optional[str] = None,
) -> List[AdoptionPet]:
    """Get all of the pets that is available for adoption"""

    try:
        query = (
            db.query(AdoptionPet)
            .join(Pet, AdoptionPet.pet_id == Pet.id)
            .options(joinedload(AdoptionPet.pet))
            .filter(AdoptionPet.deleted_at == None)
            .filter(AdoptionPet.status == "AVAILABLE")
        )

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

        query = query.offset(skip).limit(limit).all()

        return query

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


def get_adoption_pet_details(
        db: Session,
        pet_id: int
) -> Optional[AdoptionPet]:
    """
    Get a specific pet available for adoption by ID.
    
    Args:
        db: Database session
        pet_id: ID of the adoption pet record
        
    Returns:
        AdoptionPet object if found, None otherwise
    """


    return (
        db.query(AdoptionPet)
        .filter(AdoptionPet.id == pet_id)
        .filter(AdoptionPet.deleted_at == None)
        .options(joinedload(AdoptionPet.pet))
        .first()
    )

def update_pet_status(
    db: Session,
    status_update: AdoptionPetUpdateStatus,
) -> AdoptionPetInDB:
    """Update the availability of pet for adoption"""

    try:
        # Find the pet by ID
        update_adoption_pet = (
            db.query(AdoptionPet).filter(AdoptionPet.id == status_update.id).first()
        )

        # Check if pet exists
        if not update_adoption_pet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pet with ID {status_update.id} not found",
            )

        # Update the status
        update_adoption_pet.status = status_update.status

        # Commit the changes to the database
        db.commit()

        # Refresh the instance to get the updated data
        db.refresh(update_adoption_pet)

        # Return the updated pet data
        return AdoptionPetInDB.model_validate(update_adoption_pet)
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


def update_adoption_pet(
    db: Session,
    pet_update: AdoptionPetUpdate,
) -> AdoptionPetInDB:
    """Update the details of an adoption pet"""

    try:
        # Find the pet by ID
        pet = db.query(AdoptionPet).filter(AdoptionPet.id == pet_update.id).first()

        # Check if pet exists
        if not pet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pet with ID {pet_update.id} not found",
            )

        # Update fields if they are provided in the update schema
        update_data = pet_update.dict(exclude_unset=True)

        # Remove id from the update data as we don't want to update the primary key
        update_data.pop("id", None)

        # Update each field if it's provided in the update
        for key, value in update_data.items():
            # Only update if the value is not None
            if value is not None:
                setattr(pet, key, value)

        # Commit the changes to the database
        db.commit()

        # Refresh the instance to get the updated data
        db.refresh(pet)

        # Return the updated pet data
        return AdoptionPetInDB.model_validate(pet)

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
