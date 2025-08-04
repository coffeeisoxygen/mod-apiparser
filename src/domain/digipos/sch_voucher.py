"""schemas untuk Beli Voucher."""

from typing import Any

from pydantic import Field, field_validator

from domain.digipos.sch_validations import MarkUpIsZeroOrMore, PaymentMethodEnum
from src.domain.digipos.sch_pulsa import DigiposOptionalCheck
from src.shared.base_schemas import BaseDomainRequest, BaseDomainResponse


class DigiposBaseVoucherRequest(BaseDomainRequest):
    payment_method: PaymentMethodEnum = Field(
        default=PaymentMethodEnum.LINKAJA,
        description="Metode pembayaran yang digunakan.",
        examples=[PaymentMethodEnum.LINKAJA, PaymentMethodEnum.NGRS],
    )
    markup: MarkUpIsZeroOrMore | None = Field(
        default=0,
        description="Mark Up Harga nya.",
        examples=[1000, 5000, 10000],
    )


class DigiposReqListVoucher(DigiposBaseVoucherRequest):
    """Schemas untuk melihat List Voucher yang tersedia."""

    category: str = Field(
        default="VF",
        description="Kategori voucher yang ingin dilihat, defaultnya VF (Voucher Fisik).",
        examples=["VF", "BYU"],
    )

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        if v != "VF":
            raise ValueError("category hanya boleh bernilai 'VF'")
        return v


class DigiposReqBuyVoucher(DigiposBaseVoucherRequest, DigiposOptionalCheck):
    """schemas untuk pembelian voucher."""

    product_id: str = Field(
        description="ID produk paket data yang ingin dibeli.",
        examples=["1234567890"],
    )


class DigiposVoucherResponse(BaseDomainResponse):
    """Response schema for Digipos Pulsa requests."""

    data: dict[str, Any] | None = None
    price: int | None = None
    status: str | None = None
    # req, resp, paket, dll tetap bisa diterima karena extra="allow"
