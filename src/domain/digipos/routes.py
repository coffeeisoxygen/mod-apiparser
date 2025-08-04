from fastapi import APIRouter

router = APIRouter()


@router.get("/digipos")
async def get_digipos():
    return {"message": "Hello from /digipos"}


@router.get("/digipos/listpaket")
async def list_paket():
    return {"message": "Placeholder for /digipos/listpaket"}


@router.post("/digipos/belipaket")
async def beli_paket():
    return {"message": "Placeholder for /digipos/belipaket"}


@router.get("/digipos/caripaket")
async def cari_paket():
    return {"message": "Placeholder for /digipos/caripaket"}


@router.get("/digipos/listomni")
async def list_omni():
    return {"message": "Placeholder for /digipos/listomni"}


@router.post("/digipos/beliomni")
async def beli_omni():
    return {"message": "Placeholder for /digipos/beliomni"}
