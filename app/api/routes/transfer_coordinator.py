import json
import logging
from fastapi import APIRouter, Depends, Query, status
from typing import Optional
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.transfer_coordinator import PetType
from app.schemas.transfer_coordinator import (
    TransferCoordinationCreate,
    TransferCoordinationUpdate,
    TransferCoordinationResponse,
    TransferCoordinationListResponse,
    TransferCoordinationStatusUpdate
)
from app.crud.transfer_coordinator import (
    create_transfer_coordination,
    get_transfer_coordinations,
    get_transfer_coordination,
    update_transfer_coordination,
    delete_transfer_coordination,
    update_transfer_coordination_status,
)
from app.utils.redis import RedisHelper


router = APIRouter()
redis = RedisHelper()

@router.post(
    "/transfer-coordinations",
    response_model=TransferCoordinationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new transfer coordination request"
)
def create_transfer(
    *,
    transfer_in: TransferCoordinationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new transfer coordination request with:
    - **barangay_name**: Optional name of the barangay
    - **address**: Complete address for transfer
    - **pet_type**: Type of pet (Dog or Cat)
    """
    return create_transfer_coordination(
        db=db, 
        transfer_in=transfer_in, 
        current_user=current_user
    )

@router.get(
    "/transfer-coordinations",
    response_model=TransferCoordinationListResponse,
    summary="Get list of transfer coordination requests"
)
def list_transfers(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    barangay_name: Optional[str] = None,
    pet_type: Optional[PetType] = None,
    user_id: Optional[int] = None,
    # current_user: User = Depends(get_current_user)
):
    """
    Retrieve transfer coordination requests with optional filters:
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    - **barangay_name**: Filter by barangay name
    - **pet_type**: Filter by pet type (Dog/Cat)
    - **user_id**: Filter by user ID
    """
    return get_transfer_coordinations(
        db=db,
        skip=skip,
        limit=limit,
        barangay_name=barangay_name,
        pet_type=pet_type,
        user_id=user_id
    )

@router.get(
    "/transfer-coordinations/{transfer_id}",
    response_model=TransferCoordinationResponse,
    summary="Get a specific transfer coordination request"
)
def get_transfer(
    transfer_id: int,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve a specific transfer coordination request by its ID
    """
    return get_transfer_coordination(db=db, transfer_id=transfer_id)

@router.patch(
    "/transfer-coordinations/{transfer_id}",
    response_model=TransferCoordinationResponse,
    summary="Update a transfer coordination request"
)
def update_transfer(
    *,
    transfer_id: int,
    transfer_in: TransferCoordinationUpdate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_active_user)
):
    """
    Update an existing transfer coordination request.
    Only the owner or superuser can modify the request.
    """
    return update_transfer_coordination(
        db=db,
        transfer_id=transfer_id,
        transfer_in=transfer_in,
        # current_user=current_user
    )

@router.delete(
    "/transfer-coordinations/{transfer_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a transfer coordination request"
)
def delete_transfer(
    transfer_id: int,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_active_user)
):
    """
    Delete a transfer coordination request.
    Only the owner or superuser can delete the request.
    """
    return delete_transfer_coordination(
        db=db,
        transfer_id=transfer_id,
        # current_user=current_user
    )


@router.patch(
    "/transfer-coordinations/{transfer_id}/status",
    response_model=TransferCoordinationResponse,
    summary="Update transfer coordination status"
)
def update_transfer_status(
    transfer_id: int,
    status_update: TransferCoordinationStatusUpdate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_active_user)
):
    """
    Update the status of a transfer coordination request.
    
    Available statuses:
    - PENDING
    - ACCEPTED
    - IN_PROGRESS
    - COMPLETED
    - CANCELLED
    
    Only the owner or admin can update the status.
    """

    transfer = update_transfer_coordination_status(
        db=db,
        transfer_id=transfer_id,
        status_update=status_update,
        # current_user=current_user
    )

    #add redis data
    formatted_schedule = transfer.request_datetime.strftime("%B %d %Y, %I:%M %p") if transfer.request_datetime else None
    redis_data = {
        "queue_type": "transfer_notification",
        "email": transfer.user.email,
        "name": transfer.user.full_name,
        "request_data": {
            "barangay_name": transfer.barangay_name,
            "address": transfer.address,
            "pet_type": transfer.pet_type.value,
            "requested_date": formatted_schedule,
        },
    }

    transaction_queue= redis.add_to_redis_set("qc_pet_adoption:notifications", json.dumps(redis_data))


    if not transaction_queue:
        logging.warning(f"Failed to store in the queue {transfer.id}")
    # print(redis_data)
     
    return transfer