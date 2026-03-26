import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.product import Product


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id"), nullable=False
    )
    variant_label: Mapped[str] = mapped_column(String(50), nullable=False)
    price_override: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    stock_quantity: Mapped[int] = mapped_column(default=0, nullable=False)
    sku: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Relationships
    product: Mapped["Product"] = relationship(back_populates="variants")

    __table_args__ = (
        Index("ix_product_variants_product_id", "product_id"),
        Index("ix_product_variants_sku", "sku"),
    )

    def __repr__(self) -> str:
        return f"<ProductVariant {self.sku}>"
