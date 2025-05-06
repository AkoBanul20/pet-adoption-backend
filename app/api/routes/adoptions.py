import json
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.schemas.adoption import (
    AdoptionCreate,
    AdoptionListResponse,
    AdoptionUpdateStatus,
    AdoptionStatus,
    AdoptionRead,
)

from app.crud.adoption import (
    get_adoption_list,
    create_adoption_request,
    update_adoption_request_status,
)
from app.models.user import User
from app.utils.redis import RedisHelper

router = APIRouter()

redis = RedisHelper()


@router.get("/adoptions", response_model=AdoptionListResponse)
def read_adoption_list_route(
    skip: int = 0,
    limit: int = 10,
    status: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db),
):
    adoptions = get_adoption_list(db=db,skip=skip,limit=limit,status=status)

    return adoptions
@router.post("/adoptions", response_model=AdoptionRead, status_code=status.HTTP_201_CREATED)
def create_adoption_request_route(
    adoption_in: AdoptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create adoption request by user
    """
    return create_adoption_request(db=db, adoption_in=adoption_in, current_user=current_user)

@router.patch("/adoptions/{adoption_id}/status",response_model=AdoptionRead)
def update_adoption_request_status_route(
    adoption_id: int,
    status_update: AdoptionUpdateStatus,
    db: Session = Depends(get_db),
    # current_user = Depends(get_current_user)
):
    """
    Update adoption request status
    """

    update_adoption_request = update_adoption_request_status(db=db,adoption_id=adoption_id, adoption_status_in=status_update)

    formatted_schedule = update_adoption_request.schedule.strftime("%B %d %Y, %I:%M %p") if update_adoption_request.schedule else None

    redis_data = {
        "queue_type": "notification",
        "pet_image_url": update_adoption_request.adoption_pet.pet.image_url,
        "pet_name": update_adoption_request.adoption_pet.pet.name,
        "found_in": update_adoption_request.adoption_pet.found_in,
        "additional_details": update_adoption_request.adoption_pet.additional_details,
        "schedule": formatted_schedule,
        "email": update_adoption_request.adopter.email,
    }
    if update_adoption_request.status == "screening":
        adoption_request_queue = redis.add_to_redis_set("qc_pet_adoption:notifications", json.dumps(redis_data))
    
        if not adoption_request_queue:
            logging.warning(f"Failed to store in the queue {update_adoption_request.id} in redis")

    return update_adoption_request_status(db=db,adoption_id=adoption_id, adoption_status_in=status_update)
