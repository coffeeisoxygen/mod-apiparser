from enum import StrEnum
from typing import Annotated

from pydantic import BeforeValidator, Field


# =======================Khusus Payment Method=======================
class PaymentMethodEnum(StrEnum):
    """payment method yang boleh user pilih di request."""

    LINKAJA = "LINKAJA"
    NGRS = "NGRS"


def validate_linkaja_only(v: PaymentMethodEnum) -> PaymentMethodEnum:
    """Memastikan metode pembayaran hanya LINKAJA."""
    if v == PaymentMethodEnum.NGRS:
        raise ValueError("Pembelian Ini Hanya Bisa Dengan Methode LinkAJA")
    return v


LinkajaOnlyPaymentMethod = Annotated[
    PaymentMethodEnum, BeforeValidator(validate_linkaja_only)
]


def validate_ngrs_only(v: PaymentMethodEnum) -> PaymentMethodEnum:
    """Memastikan metode pembayaran hanya NGRS."""
    if v == PaymentMethodEnum.LINKAJA:
        raise ValueError("Pembelian Ini Hanya Bisa Dengan Methode NGRS")
    return v


NGRSOnlyPaymentMethod = Annotated[
    PaymentMethodEnum, BeforeValidator(validate_ngrs_only)
]


def validate_both_payment_valid(v: PaymentMethodEnum) -> PaymentMethodEnum:
    """Pembayaran boleh yang mana aja."""
    """Memastikan metode pembayaran valid untuk kedua kategori."""
    if v not in (PaymentMethodEnum.LINKAJA, PaymentMethodEnum.NGRS):
        raise ValueError("Pembelian Ini Hanya Bisa Dengan Methode LinkAJA atau NGRS")
    return v


BothPaymentValid = Annotated[
    PaymentMethodEnum, BeforeValidator(validate_both_payment_valid)
]

# =====================


def validate_param_check(v: int) -> int:
    """Validasi parameter check, hanya boleh 1 atau 0."""
    if v not in (0, 1):
        raise ValueError("Field 'check' hanya boleh bernilai 0 atau 1.")
    return v


CheckFieldIsZeroOrOne = Annotated[
    int, Field(description="Check 0/1"), BeforeValidator(validate_param_check)
]


def validate_markup(v: int) -> int:
    """Validasi markup harga, hanya boleh 0 atau lebih besar."""
    if v < 0:
        raise ValueError("Markup harga hanya boleh 0 atau lebih besar.")
    return v


MarkUpIsZeroOrMore = Annotated[
    int,
    Field(description="Markup harga untuk paket data"),
    BeforeValidator(validate_markup),
]
