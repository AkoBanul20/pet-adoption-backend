from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth
from app.api.routes import pets, lost_pets
from app.core.config import settings

app = FastAPI(
    title=settings.SERVER_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(pets.router, prefix=f"{settings.API_V1_STR}/pet", tags=["pets"])
app.include_router(
    lost_pets.router, prefix=f"{settings.API_V1_STR}/lost-pet", tags=["lost pets"]
)
