from fastapi import APIRouter

router = APIRouter()


@router.get("/digipos")
async def get_digipos():
    return {"message": "Hello from /digipos"}
