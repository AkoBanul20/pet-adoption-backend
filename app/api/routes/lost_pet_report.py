import os
import json
import logging
from pathlib import Path
from uuid import uuid4
import shutil
from typing import Any, List, Optional
from typing_extensions import Annotated
from fastapi import APIRouter, Depends, status, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.crud.lost_pet_report import (
    create_lost_pet_report,
    get_lost_pet_reports,
    get_lost_pet_report_by_id,
)
from app.schemas.lost_pet_report import (
    LostPetReport,
    LostPetReportCreate,
    LostPetReportDetailsResponse,
)

from app.models.user import User

# from app.tasks.lost_pet_report import send_lost_pet_report_to_redis
from app.utils.redis import RedisHelper

router = APIRouter()


UPLOAD_DIR = Path("app/static/uploads/lost_pet_reports")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

STATIC_URL_BASE = "/static/uploads/lost_pet_reports"

redis = RedisHelper()


@router.post("/add", response_model=LostPetReport, status_code=status.HTTP_201_CREATED)
def create_lost_pet_report_route(
    *,
    db: Session = Depends(get_db),
    lost_pet_id: int = Form(...),
    reporter_id: int = Form(...),
    details: str = Form(...),
    report_location: str = Form(...),
    image_file: Annotated[UploadFile, File()],
    current_user: User = Depends(get_current_user),
) -> Any:
    """Create lost pet report"""

    image_url = None
    # handle image upload if a file is provided
    if image_file and image_file.filename:
        try:
            # Validate file type
            if image_file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid File Type. Only JPEG and PNG are allowed.",
                )

            # USER DIRECTORY
            user_id = current_user.id
            username = current_user.username
            USER_FOLDER = f"{str(user_id)}/{str(username)}"
            USER_DIR = UPLOAD_DIR / str(user_id) / str(username)
            USER_DIR.mkdir(parents=True, exist_ok=True)


            # Create a unique filename to prevent overwriting
            file_extension =  os.path.splitext(image_file.filename)[1]
            filename = f"{uuid4()}{file_extension}"

            # Save the file
            file_path = USER_DIR / filename
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(image_file.file, buffer)

            # Generate a URL that can be accessed via your API
            image_url = f"{STATIC_URL_BASE}/{USER_FOLDER}/{filename}"

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error uploading image: {str(e)}"
            )

    lost_pet_report_data = {
        "lost_pet_id": lost_pet_id,
        "reporter_id": reporter_id,
        "details": details,
        "report_location": report_location,
        "image_url": image_url,
    }

    created_lost_pet_report = create_lost_pet_report(
        db=db,
        lost_pet_report_in=LostPetReportCreate(**lost_pet_report_data),
    )

    # data for redis queue

    redis_data = {
        "report_id": created_lost_pet_report.id,
        "pet_image_url": created_lost_pet_report.lost_pet.pet.image_url,
        "report_image_url": created_lost_pet_report.image_url,
        "reporter_details": {
            "id": created_lost_pet_report.reporter.id,
            "username": created_lost_pet_report.reporter.username,
            "email": created_lost_pet_report.reporter.email,
        },
        "owner_details": {
            "id": created_lost_pet_report.lost_pet.pet.owner.id,
            "username": created_lost_pet_report.lost_pet.pet.owner.username,
            "email": created_lost_pet_report.lost_pet.pet.owner.email,
        },
    }

    success_queue = redis.add_to_redis_set("qc_pet_adoption:lost_pet_reports", json.dumps(redis_data))
    
    if not success_queue:
        logging.warning(f"Failed to store report {created_lost_pet_report.id} in Redis")
        pass

    return created_lost_pet_report


@router.get(
    "/list",
    response_model=List[LostPetReportDetailsResponse],
    status_code=status.HTTP_200_OK,
)
def read_lost_pet_reports_route(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 0,
) -> Any:
    """
    Retrieve all lost pet reports.
    """

    lost_pet_reports = get_lost_pet_reports(db=db, skip=skip, limit=limit)

    return lost_pet_reports


@router.get(
    "/{report_id}",
    response_model=LostPetReportDetailsResponse,
    status_code=status.HTTP_200_OK,
)
def read_lost_pet_report_route(
    *,
    db: Session = Depends(get_db),
    report_id: int,
) -> Any:
    """
    Retrieve a specific lost pet report by ID.
    """

    lost_pet_report = get_lost_pet_report_by_id(db=db, lost_pet_report_id=report_id)

    if not lost_pet_report:
        raise HTTPException(status_code=404, detail="Lost pet report not found")

    return lost_pet_report
