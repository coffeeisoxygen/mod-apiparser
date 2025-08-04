from fastapi import APIRouter

from src.domain.digipos.routes import router as digipos_router

api_router = APIRouter()
api_router.include_router(
    router=digipos_router,
    prefix="/digipos",  # <-- set prefix di sini
    tags=["digipos"],  # <-- set tags di sini
)

# ...you can include more routers here as needed...
