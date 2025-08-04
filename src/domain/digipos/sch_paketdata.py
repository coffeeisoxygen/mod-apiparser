from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator

from domain.digipos.sch_validations import (
    CheckFieldIsZeroOrOne,
    LinkajaOnlyPaymentMethod,
    MarkUpIsZeroOrMore,
    PaymentMethodEnum,
)
from src.shared.base_schemas import BaseDomainRequest, BaseDomainResponse


class PackageCategoryEnum(StrEnum):
    """category yang boleh user pilih di request."""

    DATA = "DATA"
    VOICE_SMS = "VOICE_SMS"
    DIGITAL_OTHER = "DIGITAL_OTHER"
    DIGITAL_MUSIC = "DIGITAL_MUSIC"
    DIGITAL_GAME = "DIGITAL_GAME"
    ROAMING = "ROAMING"
    VF = "VF"
    BYU = "BYU"
    HVC_DATA = "HVC_DATA"
    HVC_VOICE_SMS = "HVC_VOICE_SMS"


class DigiposBasePackageRequest(BaseDomainRequest):
    """common shared Schemas , biar ngga Dry Aja Sih."""

    category: PackageCategoryEnum = Field(
        description="Kategori paket yang ingin dilihat, seperti DATA, VOICE_SMS, DIGITAL_OTHER, dll.",
        examples=[PackageCategoryEnum.DATA, PackageCategoryEnum.VOICE_SMS],
    )

    payment_method: LinkajaOnlyPaymentMethod = Field(
        description="Metode pembayaran yang digunakan, seperti LINKAJA atau NGRS.",
        examples=[PaymentMethodEnum.LINKAJA, PaymentMethodEnum.NGRS],
    )

    markup: MarkUpIsZeroOrMore | None = Field(
        default=0,
        description="Markup harga untuk paket data.",
        examples=[0, 10000],
    )


class DigiposOptionalCheck(BaseModel):
    check: CheckFieldIsZeroOrOne = Field(
        description="Jika Check=1, Maka Akan menjadi Mode Postpaid, dan Check=0 akan menjadi mode direct transaction tanpa check",
        examples=[1, 0],
    )


class DigiposReqListPaketData(DigiposBasePackageRequest):
    """Request Schemas ketika user ingin memlihat List Paket eligible untuk nomor tujuan."""

    sub_category: str | None = Field(
        default=None,
        description="Subkategori produk, jika ada. Misalnya, untuk kategori DATA bisa berupa Combo Sakti Dan Lain Lain.",
        examples=["Combo Sakti", "Lain Lain", None],
    )

    duration: str | None = Field(
        default=None,
        description="Durasi paket, jika ada. Misalnya, '30 hari', '7 hari'.",
        examples=["30 Days", "7 Days", None],
    )

    kolom: list[str] = Field(
        default_factory=lambda: ["productId", "productName", "quota", "total_"]
    )

    @model_validator(mode="after")
    def validate_required_kolom(self) -> "DigiposReqListPaketData":
        required = {"productId", "productName", "quota", "total_"}
        if not required.issubset(set(self.kolom)):
            missing = required - set(self.kolom)
            raise ValueError(
                f"Field kolom harus mengandung minimal: {', '.join(required)}. Missing: {', '.join(missing)}"
            )
        return self


class DigiposReqBuyPaketData(DigiposBasePackageRequest, DigiposOptionalCheck):
    """Request Schemas ketika user ingin membeli Paket Data."""

    product_id: str = Field(
        description="ID produk paket data yang ingin dibeli.",
        examples=["1234567890"],
    )


class DigiposResponse(BaseDomainResponse):
    """Response Schema untuk Digipos."""

    req: dict[str, Any] | None = None
    resp: list[dict[str, Any]] | None = None
    paket: list[dict[str, Any]] | None = None
