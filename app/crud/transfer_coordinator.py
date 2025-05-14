from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException, status

from app.models.transfer_coordinator import TransferCoordination, PetType
from app.models.user import User
from app.schemas.transfer_coordinator import TransferCoordinationCreate, TransferCoordinationUpdate, TransferCoordinationStatusUpdate, TransferCoordinationInDB

def create_transfer_coordination(
    db: Session,
    transfer_in: TransferCoordinationCreate,
    current_user: User
) -> TransferCoordination:
    """Create a new transfer coordination request"""
    try:
        db_transfer = TransferCoordination(
            barangay_name=transfer_in.barangay_name,
            address=transfer_in.address,
            pet_type=transfer_in.pet_type,
            status="PENDING",
            user_id=current_user.id,
            request_datetime=transfer_in.request_datetime
        )
        
        db.add(db_transfer)
        db.commit()
        db.refresh(db_transfer)
        
        return db_transfer
    
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

def get_transfer_coordinations(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    barangay_name: Optional[str] = None,
    pet_type: Optional[PetType] = None,
    user_id: Optional[int] = None,
    status: Optional[int] = None
) -> dict:
    """Get list of transfer coordination requests with optional filters"""
    try:
        query = db.query(TransferCoordination)

        if barangay_name:
            query = query.filter(TransferCoordination.barangay_name == barangay_name)
        if pet_type:
            query = query.filter(TransferCoordination.pet_type == pet_type)
        if user_id:
            query = query.filter(TransferCoordination.user_id == user_id)
        if status:
            query = query.filter(TransferCoordination,status == status)

        total = query.count()
        transfers = query.order_by(TransferCoordination.request_datetime.desc()) \
                       .offset(skip).limit(limit).all()

        return {"items": transfers, "total": total}

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

def get_transfer_coordination(
    db: Session,
    transfer_id: int
) -> TransferCoordination:
    """Get a specific transfer coordination request by ID"""
    transfer = db.query(TransferCoordination) \
                 .filter(TransferCoordination.id == transfer_id) \
                 .first()
    
    if not transfer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transfer coordination with ID {transfer_id} not found"
        )
    
    return transfer

def update_transfer_coordination(
    db: Session,
    transfer_id: int,
    transfer_in: TransferCoordinationUpdate,
    # current_user: User
) -> TransferCoordination:
    """Update an existing transfer coordination request"""
    try:
        transfer = get_transfer_coordination(db, transfer_id)
        
        # Check if user owns this transfer request
        # if transfer.user_id != current_user.id and not current_user.is_superuser:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Not authorized to modify this transfer coordination request"
        #     )

        update_data = transfer_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(transfer, field, value)

        db.commit()
        db.refresh(transfer)
        return transfer

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

def delete_transfer_coordination(
    db: Session,
    transfer_id: int,
    # current_user: User
) -> dict:
    """Delete a transfer coordination request"""
    try:
        transfer = get_transfer_coordination(db, transfer_id)
        
        # # Check if user owns this transfer request
        # if transfer.user_id != current_user.id and not current_user.is_superuser:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Not authorized to delete this transfer coordination request"
        #     )

        db.delete(transfer)
        db.commit()
        
        return {"message": "Transfer coordination request deleted successfully"}

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    

def update_transfer_coordination_status(
    db: Session,
    transfer_id: int,
    status_update: TransferCoordinationStatusUpdate,
    # current_user: User,
) -> TransferCoordination:
    """Update the status of a transfer coordination request"""
    try:
        transfer = db.query(TransferCoordination).filter(
            TransferCoordination.id == transfer_id,
            TransferCoordination.deleted_at.is_(None)
        ).first()

        if not transfer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Transfer coordination with ID {transfer_id} not found"
            )

        # # Check if user is authorized (owner or admin)
        # if transfer.user_id != current_user.id and not current_user.is_superuser:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Not authorized to update this transfer coordination status"
        #     )

        # Validate status value
        valid_statuses = ["PENDING", "APPROVED", "IN_PROGRESS", "COMPLETED", "CANCELLED"]
        if status_update.status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )

        transfer.status = status_update.status
        db.commit()
        db.refresh(transfer)

        return TransferCoordinationInDB.model_validate(transfer)

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )