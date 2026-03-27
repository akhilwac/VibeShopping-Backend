from fastapi import APIRouter

from app.api.v1.routes import (
    addresses,
    admin,
    auth,
    banners,
    cart,
    categories,
    orders,
    payment_methods,
    payments,
    products,
    reviews,
    users,
    wishlist,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(categories.router)
api_router.include_router(products.router)
api_router.include_router(wishlist.router)
api_router.include_router(cart.router)
api_router.include_router(orders.router)
api_router.include_router(payments.router)
api_router.include_router(addresses.router)
api_router.include_router(payment_methods.router)
api_router.include_router(reviews.router)
api_router.include_router(banners.router)
api_router.include_router(admin.router)
