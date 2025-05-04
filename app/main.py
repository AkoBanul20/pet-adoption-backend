import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.routes import auth
from app.api.routes import pets, lost_pets, lost_pet_report, adoption_pet
from app.utils.constants import (SERVER_NAME, API_V1_STR, API_ROOT_PATH,)

app = FastAPI(
    title=SERVER_NAME, 
    openapi_url="/openapi.json",  # Schema will be at /api/openapi.json
    docs_url="/docs",            # Swagger UI at /api/docs
    redoc_url="/redoc",
    root_path=API_ROOT_PATH,  # All routes will be prefixed with /api 
)

# Set all CORS enabled origins
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    "https://qcacac.site",
    "https://qcacac.site/api"

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("app/static/uploads", exist_ok=True)
# Mount 'app/static' to serve at '/static'
static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path, html=True), name="static")

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the API", "status": "active"}

# Health check point
@app.get("/health")
def health_check():
    return {"status": "healthy"}


# Include routers
app.include_router(auth.router, prefix=f"{API_V1_STR}/auth", tags=["auth"])
app.include_router(pets.router, prefix=f"{API_V1_STR}/pet", tags=["pets"])
app.include_router(
    lost_pets.router, prefix=f"{API_V1_STR}/lost-pet", tags=["lost pets"]
)
app.include_router(lost_pet_report.router, prefix=f"{API_V1_STR}/lost-pet-report", tags=["lost pet report"])
app.include_router(adoption_pet.router, prefix=f"{API_V1_STR}/adoption-pet", tags=["pet for adoption"])