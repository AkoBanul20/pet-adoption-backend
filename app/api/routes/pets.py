import os
import shutil
from datetime import datetime
from typing import Any, List, Optional
from typing_extensions import Annotated
from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    status,
    File,
    UploadFile,
    Form,
)
from sqlalchemy.orm import Session
from pathlib import Path
from uuid import uuid4


from app.core.database import get_db
from app.api.deps import get_current_user
from app.crud.pet import (
    create_pet,
    update_pet,
    search_pets,
    get_pets,
    get_pet,
    get_pets_by_owner,
    get_pets_count,
)
from app.schemas.pet import Pet, PetCreate, PetsByOwner, PetListResponse
from app.models.user import User

router = APIRouter()

UPLOAD_DIR = Path("app/static/uploads/pets")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

STATIC_URL_BASE = "/static/uploads/pets"


@router.post("/add", response_model=Pet, status_code=status.HTTP_201_CREATED)
def create_pet_route(
    *,
    db: Session = Depends(get_db),
    type: str = Form(...),
    name: Optional[str] = Form(None),
    breed: Optional[str] = Form(None),
    gender: Optional[str] = Form(None),
    age: Optional[str] = Form(None),
    color: str = Form(...),
    size: str = Form(...),
    description: str = Form(...),
    image_file: Annotated[UploadFile, File()],
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create new pet record
    """

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
            file_extension = os.path.splitext(image_file.filename)[1]
            filename = f"{uuid4()}{file_extension}"

            # Save the file
            file_path = USER_DIR / filename
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(image_file.file, buffer)

            # Generate a URL that can be accessed via your API
            image_url = f"{STATIC_URL_BASE}/{USER_FOLDER}/{filename}"

        except Exception as e:
            # Handle unexpected errors
            raise HTTPException(
                status_code=500, detail=f"Error uploading image: {str(e)}"
            )

    # pet_in.image_url = image_url
    pet_data = {
        "type": type,
        "name": name,
        "breed": breed,
        "gender": gender,
        "age": age,
        "color": color,
        "size": size,
        "description": description,
        "image_url": image_url,
    }

    created_pet = create_pet(
        db=db,
        pet_in=PetCreate(**pet_data),
        current_user=current_user,
    )
    return created_pet


@router.get("/list", response_model=PetListResponse)
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

    # Get the total count of pets ()
    total = get_pets_count(
        db,
        skip=skip,
        limit=limit,
        type=type,
        gender=gender,
        breed=breed,
        color=color,
        added_by_admin=admin_featured,
    )

    return {
        "items": pets,
        "total": total,
    }


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
