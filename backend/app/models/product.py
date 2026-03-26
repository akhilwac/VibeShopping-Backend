import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.product_image import ProductImage
    from app.models.product_variant import ProductVariant
    from app.models.review import Review


class Product(TimestampMixin, Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("categories.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    base_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    avg_rating: Mapped[Decimal] = mapped_column(
        Numeric(2, 1), default=Decimal("0.0"), nullable=False
    )
    review_count: Mapped[int] = mapped_column(default=0, nullable=False)
    is_featured: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Relationships
    category: Mapped["Category"] = relationship(back_populates="products")
    variants: Mapped[list["ProductVariant"]] = relationship(
        back_populates="product", cascade="all, delete-orphan", lazy="raise"
    )
    images: Mapped[list["ProductImage"]] = relationship(
        back_populates="product", cascade="all, delete-orphan", lazy="raise"
    )
    reviews: Mapped[list["Review"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_products_category_id", "category_id"),
        Index("ix_products_is_featured", "is_featured"),
        Index("ix_products_created_at", "created_at"),
        Index("ix_products_active_created", "is_active", "created_at"),
        Index("ix_products_cat_active_created", "category_id", "is_active", "created_at"),
    )

    @property
    def primary_image_url(self) -> str | None:
        """Return the primary image URL, falling back to the first image."""
        for img in self.images:
            if img.is_primary:
                return img.image_url
        return self.images[0].image_url if self.images else None

    def __repr__(self) -> str:
        return f"<Product {self.name}>"
