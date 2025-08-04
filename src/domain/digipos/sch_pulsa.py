from enum import StrEnum
from typing import Any

from pydantic import Field, PositiveInt, model_validator

from domain.digipos.sch_validations import (
    LinkajaOnlyPaymentMethod,
    MarkUpIsZeroOrMore,
    PaymentMethodEnum,
)
from src.domain.digipos.sch_paketdata import DigiposOptionalCheck
from src.shared.base_schemas import BaseDomainRequest, BaseDomainResponse


class PulsaPackageCategoryEnum(StrEnum):
    """category yang boleh user pilih di request."""

    FIX = "FIX"
    BULK = "BULK"


class DigiposReqListPulsa(BaseDomainRequest):
    """schemas untuk melihat List Pulsa."""

    amount: PositiveInt = Field(
        description="Jumlah pulsa yang ingin dibeli, biasanya dalam satuan ribu.",
        examples=[1000, 5000, 10000],
    )
    payment_method: LinkajaOnlyPaymentMethod = Field(
        description="Metode pembayaran yang digunakan, seperti LINKAJA atau NGRS. Untuk List Ini Haru LinkAja.",
        examples=[PaymentMethodEnum.LINKAJA, PaymentMethodEnum.NGRS],
    )

    markup: MarkUpIsZeroOrMore | None = Field(
        default=0,
        description="Mark Up Harga nya.",
        examples=[1000, 5000, 10000],
    )


class DigiposReqBuyPulsa(BaseDomainRequest, DigiposOptionalCheck):
    """schemas untuk membeli pulsa."""

    category: PulsaPackageCategoryEnum = Field(
        description="Kategori pulsa yang ingin dibeli, seperti FIX atau BULK.",
        examples=[PulsaPackageCategoryEnum.FIX, PulsaPackageCategoryEnum.BULK],
    )

    payment_method: PaymentMethodEnum = Field(
        description="Metode pembayaran yang digunakan, seperti LINKAJA atau NGRS.",
        examples=[PaymentMethodEnum.LINKAJA, PaymentMethodEnum.NGRS],
    )
    markup: MarkUpIsZeroOrMore | None = Field(
        default=0,
        description="Harga Untuk Melakukan Markup kepada harga pulsa.",
        examples=[0, 10000],
    )

    @model_validator(mode="after")
    def validate_category_payment(self) -> "DigiposReqBuyPulsa":
        if (
            self.category == PulsaPackageCategoryEnum.FIX
            and self.payment_method != PaymentMethodEnum.NGRS
        ):
            raise ValueError("Jika category FIX, payment_method wajib NGRS.")
        if (
            self.category == PulsaPackageCategoryEnum.BULK
            and self.payment_method != PaymentMethodEnum.LINKAJA
        ):
            raise ValueError("Jika category BULK, payment_method wajib LINKAJA.")
        return self


class DigiposPulsaResponse(BaseDomainResponse):
    """Response schema for Digipos Pulsa requests."""

    data: dict[str, Any] | None = None
    price: int | None = None
    status: str | None = None
    # req, resp, paket, dll tetap bisa diterima karena extra="allow"
