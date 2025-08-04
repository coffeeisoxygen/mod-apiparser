from fastapi import APIRouter, Depends

from dependencies.mod_depends import AccountService, get_account_service
from domain.digipos.sch_paketdata import (
    DigiposReqBuyPaketData,
    DigiposReqListPaketData,
    DigiposResponse,
)

router = APIRouter()


@router.get("/")
async def get_digipos():
    return {"message": "Hello from /digipos"}


@router.post("/listpaket", response_model=DigiposResponse)
async def list_paket(
    req: DigiposReqListPaketData,
    account_service: AccountService = Depends(get_account_service),
):
    # Dummy response, replace with actual logic
    return DigiposResponse(
        req=req.model_dump(),
        resp=None,
        paket=[
            {
                "productId": "123",
                "productName": "Paket Data 10GB",
                "quota": "10GB",
                "total_": 50000,
            }
        ],
    )


@router.post("/belipaket", response_model=DigiposResponse)
async def beli_paket(req: DigiposReqBuyPaketData):
    return {"message": "Placeholder for /belipaket"}


@router.get("/caripaket", response_model=DigiposResponse)
async def cari_paket():
    return {"message": "Placeholder for /caripaket"}


@router.get("/listomni", response_model=DigiposResponse)
async def list_omni():
    return {"message": "Placeholder for /listomni"}


@router.post("/beliomni")
async def beli_omni():
    return {"message": "Placeholder for /digipos/beliomni"}
