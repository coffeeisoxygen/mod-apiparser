from fastapi import APIRouter

from src.domain.digipos.routes import router as digipos_router

api_router = APIRouter()
api_router.include_router(digipos_router)

# ...you can include more routers here as needed...
