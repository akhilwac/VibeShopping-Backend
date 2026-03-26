import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.product_variant import ProductVariant
    from app.models.user import User


class CartItem(TimestampMixin, Base):
    __tablename__ = "cart_items"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    variant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("product_variants.id"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="cart_items")
    variant: Mapped["ProductVariant"] = relationship(lazy="selectin")

    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_cart_items_quantity_positive"),
        UniqueConstraint("user_id", "variant_id", name="uq_cart_user_variant"),
        Index("ix_cart_items_user_id", "user_id"),
    )

    def __repr__(self) -> str:
        return f"<CartItem user={self.user_id} variant={self.variant_id} qty={self.quantity}>"
