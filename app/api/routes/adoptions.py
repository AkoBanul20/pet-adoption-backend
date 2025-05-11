import os
import json
import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from docxtpl import DocxTemplate
import tempfile

from app.core.database import get_db
from app.api.deps import get_current_user
from app.schemas.adoption import (
    AdoptionCreate,
    AdoptionListResponse,
    AdoptionUpdateStatus,
    AdoptionStatus,
    AdoptionRead,
    AdoptionDocumentGeneration,
)

from app.crud.adoption import (
    get_adoption_list,
    create_adoption_request,
    update_adoption_request_status,
    get_adoption_data,
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

# generate document contract
@router.post("/generate-document/", status_code=status.HTTP_201_CREATED)
def generate_contract_document(
    adoption_id: AdoptionDocumentGeneration,
    db: Session = Depends(get_db)
):
    """
    Generate document contract.
    """
    adoption_details = get_adoption_data(db=db, adoption_id=adoption_id.adoption_id)

    if not adoption_details:
        raise HTTPException(status_code=404, detail="Adoption details is not found")
    
    # data to pass in the document
    context = {
        "pet_breed": adoption_details.adoption_pet.pet.breed,
        "pet_color": adoption_details.adoption_pet.pet.color,
        "pet_gender": adoption_details.adoption_pet.pet.gender,
        "pet_type": adoption_details.adoption_pet.pet.type,
        "pet_name": adoption_details.adoption_pet.pet.name,
        "adopter": adoption_details.adopter.full_name,
        "contact_no": adoption_details.adopter.contact,
        "address": f"{adoption_details.adopter.home_street} {adoption_details.adopter.city}",
        "date": f"{datetime.now().strftime('%B, %d %Y')}"
    }

    template_path = "app/templates/Adoption_Contract_Template.docx" 

    try:
        doc = DocxTemplate(template_path)

        doc.render(context)

        # Create a temporary file to store the output
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            temp_path = tmp.name
            doc.save(temp_path)

        # Return the file as a download
        filename = f"{context['adopter'].replace(' ', '_')}_adoption_contract_document.docx"
        return FileResponse(
            path=temp_path, 
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

        
    except BaseException as e:
        logging.error(f"Error in generating document")
        # Clean up temporary file if it exists
        if 'temp_path' in locals():
            os.unlink(temp_path)
        raise HTTPException(status_code=500, detail=f"Document generation failed: {str(e)}")
    

    # return adoption_details