"""
Seed script for VibeShopping database.
Populates categories, products, variants, images, banners, and a demo user
matching the UI screens from Paper MCP.

Usage: python seed.py
"""

import asyncio
import uuid
from decimal import Decimal

from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.address import Address
from app.models.banner import Banner
from app.models.category import Category
from app.models.product import Product
from app.models.product_image import ProductImage
from app.models.product_variant import ProductVariant
from app.models.user import User


async def seed():
    async with AsyncSessionLocal() as db:
        # ── Clear existing data (order matters for foreign keys) ──
        from sqlalchemy import text

        await db.execute(text("DELETE FROM product_images"))
        await db.execute(text("DELETE FROM product_variants"))
        await db.execute(text("DELETE FROM products"))
        await db.execute(text("DELETE FROM banners"))
        await db.execute(text("DELETE FROM categories"))
        await db.execute(text("DELETE FROM addresses"))
        await db.execute(text("DELETE FROM users WHERE id = 'a1000000-0000-0000-0000-000000000001'"))
        await db.commit()

        # ── Demo User ──────────────────────────────────────────────
        demo_user = User(
            id=uuid.UUID("a1000000-0000-0000-0000-000000000001"),
            full_name="Akhil",
            email="akhil@vibeshopping.com",
            phone="+919876543210",
            password_hash=hash_password("Password123!"),
            auth_provider="email",
        )
        db.add(demo_user)

        # Demo address
        db.add(Address(
            user_id=demo_user.id,
            label="Home",
            address_line1="42 MG Road",
            address_line2="Near Metro Station",
            city="Kochi",
            state="Kerala",
            postal_code="682001",
            country="India",
            is_default=True,
        ))

        # ── Categories (from Home + Categories screens) ────────────
        categories_data = [
            ("Fashion", "https://img.icons8.com/fluency/96/clothes.png", 1),
            ("Furniture", "https://img.icons8.com/fluency/96/armchair.png", 2),
            ("Electronics", "https://img.icons8.com/fluency/96/electronics.png", 3),
            ("Beauty", "https://img.icons8.com/fluency/96/lipstick.png", 4),
            ("Sports", "https://img.icons8.com/fluency/96/sport.png", 5),
            ("Accessories", "https://img.icons8.com/fluency/96/watch.png", 6),
            ("Books", "https://img.icons8.com/fluency/96/book.png", 7),
        ]

        cats = {}
        for name, icon, order in categories_data:
            cat = Category(
                id=uuid.uuid5(uuid.NAMESPACE_DNS, f"category-{name}"),
                name=name,
                icon_url=icon,
                sort_order=order,
            )
            db.add(cat)
            cats[name] = cat

        # ── Products ───────────────────────────────────────────────
        # Products from Home Featured section + Product List screen
        products_data = [
            # (name, category, price, rating, review_count, featured, description, image_url, variants)
            (
                "Minimal Backpack",
                "Fashion",
                Decimal("89.99"),
                Decimal("4.5"),
                312,
                True,
                "A sleek, minimalist backpack crafted from premium water-resistant fabric. Perfect for daily commutes and weekend adventures. Features padded laptop compartment and hidden anti-theft pocket.",
                "https://drive.google.com/file/d/1w9Joz6cine-gCQw85TGqsB-oZrQggJOV/view?usp=sharing",
                [("Color: Black", None, 45, "BAG-MIN-BLK"), ("Color: Gray", None, 32, "BAG-MIN-GRY"), ("Color: Navy", None, 18, "BAG-MIN-NVY")],
            ),
            (
                "Wireless Earbuds",
                "Electronics",
                Decimal("129.00"),
                Decimal("4.7"),
                856,
                True,
                "Premium true wireless earbuds with active noise cancellation, 30-hour battery life, and crystal-clear audio. IPX5 water resistant with touch controls.",
                "https://images.unsplash.com/photo-1590658268037-6bf12f032f55?w=400",
                [("Color: White", None, 120, "EAR-WL-WHT"), ("Color: Black", None, 95, "EAR-WL-BLK")],
            ),
            (
                "Denim Jacket",
                "Fashion",
                Decimal("149.00"),
                Decimal("4.7"),
                234,
                False,
                "Classic denim jacket with a modern relaxed fit. Made from premium selvedge denim that ages beautifully. Brass buttons and reinforced stitching throughout.",
                "https://images.unsplash.com/photo-1576995853123-5a10305d93c0?w=400",
                [("Size: S", None, 15, "JKT-DNM-S"), ("Size: M", None, 28, "JKT-DNM-M"), ("Size: L", None, 22, "JKT-DNM-L"), ("Size: XL", None, 10, "JKT-DNM-XL")],
            ),
            (
                "Summer Dress",
                "Fashion",
                Decimal("79.00"),
                Decimal("4.9"),
                512,
                False,
                "Light and flowy summer dress in a beautiful floral print. Made from breathable cotton-linen blend. Features adjustable straps and side pockets.",
                "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=400",
                [("Size: XS", None, 10, "DRS-SUM-XS"), ("Size: S", None, 20, "DRS-SUM-S"), ("Size: M", None, 25, "DRS-SUM-M"), ("Size: L", None, 15, "DRS-SUM-L")],
            ),
            (
                "Running Shoes",
                "Sports",
                Decimal("199.00"),
                Decimal("4.5"),
                189,
                False,
                "Lightweight performance running shoes with responsive cushioning and breathable mesh upper. Designed for neutral runners seeking speed and comfort.",
                "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400",
                [("Size: 8", None, 12, "SHO-RUN-8"), ("Size: 9", None, 18, "SHO-RUN-9"), ("Size: 10", None, 22, "SHO-RUN-10"), ("Size: 11", None, 14, "SHO-RUN-11")],
            ),
            (
                "Silk Scarf",
                "Accessories",
                Decimal("45.00"),
                Decimal("4.3"),
                87,
                False,
                "Luxurious 100% mulberry silk scarf with hand-rolled edges. Versatile styling — wear as a neck scarf, headband, or bag accent. Comes in a gift box.",
                "https://images.unsplash.com/photo-1601924638867-3a6de6b7a500?w=400",
                [("Color: Rose", None, 30, "SCF-SLK-RSE"), ("Color: Blue", None, 25, "SCF-SLK-BLU"), ("Color: Ivory", None, 20, "SCF-SLK-IVR")],
            ),
            (
                "Smart Watch Pro",
                "Electronics",
                Decimal("349.00"),
                Decimal("4.6"),
                1203,
                True,
                "Advanced smartwatch with AMOLED display, heart rate monitor, GPS, and 7-day battery life. Tracks 100+ workout modes with swim-proof design.",
                "https://images.unsplash.com/photo-1546868871-af0de0ae72be?w=400",
                [("Band: Black Sport", None, 50, "WCH-PRO-BLK"), ("Band: Silver Metal", Decimal("399.00"), 30, "WCH-PRO-SLV")],
            ),
            (
                "Ceramic Vase Set",
                "Furniture",
                Decimal("65.00"),
                Decimal("4.4"),
                156,
                True,
                "Set of 3 handcrafted ceramic vases in complementary earth tones. Each piece is uniquely glazed. Perfect for dried flowers or as standalone decor.",
                "https://images.unsplash.com/photo-1578500494198-246f612d3b3d?w=400",
                [("Style: Earth Tones", None, 40, "VAS-CRM-ETH"), ("Style: Ocean Blue", None, 35, "VAS-CRM-OCN")],
            ),
            (
                "Yoga Mat Premium",
                "Sports",
                Decimal("59.99"),
                Decimal("4.8"),
                678,
                False,
                "Extra-thick 6mm natural rubber yoga mat with alignment lines. Non-slip on both sides, moisture-wicking surface. Includes carrying strap.",
                "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=400",
                [("Color: Sage", None, 55, "YGA-MAT-SGE"), ("Color: Midnight", None, 40, "YGA-MAT-MID"), ("Color: Coral", None, 30, "YGA-MAT-CRL")],
            ),
            (
                "Vitamin C Serum",
                "Beauty",
                Decimal("34.99"),
                Decimal("4.6"),
                2341,
                True,
                "Clinical-strength 20% Vitamin C serum with hyaluronic acid and vitamin E. Brightens skin, reduces dark spots, and boosts collagen production.",
                "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=400",
                [("Size: 30ml", None, 200, "SRM-VTC-30"), ("Size: 60ml", Decimal("54.99"), 100, "SRM-VTC-60")],
            ),
            (
                "Leather Wallet",
                "Accessories",
                Decimal("89.00"),
                Decimal("4.5"),
                445,
                False,
                "Full-grain leather bifold wallet with RFID blocking technology. Features 8 card slots, 2 bill compartments, and a coin pocket. Ages beautifully over time.",
                "https://images.unsplash.com/photo-1627123424574-724758594e93?w=400",
                [("Color: Tan", None, 60, "WLT-LTH-TAN"), ("Color: Black", None, 55, "WLT-LTH-BLK"), ("Color: Burgundy", None, 35, "WLT-LTH-BRG")],
            ),
            (
                "Bluetooth Speaker",
                "Electronics",
                Decimal("79.99"),
                Decimal("4.4"),
                923,
                False,
                "Portable waterproof Bluetooth speaker with 360° surround sound and 24-hour playtime. Built-in microphone for hands-free calls. Pairs two for stereo.",
                "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=400",
                [("Color: Black", None, 80, "SPK-BT-BLK"), ("Color: Teal", None, 45, "SPK-BT-TEL"), ("Color: Red", None, 35, "SPK-BT-RED")],
            ),
            (
                "Wooden Desk Lamp",
                "Furniture",
                Decimal("95.00"),
                Decimal("4.7"),
                267,
                False,
                "Scandinavian-inspired desk lamp with solid oak base and adjustable brass arm. Warm LED bulb included. Touch-dimming with 3 brightness levels.",
                "https://images.unsplash.com/photo-1507473885765-e6ed057ab6fe?w=400",
                [("Finish: Natural Oak", None, 25, "LMP-DSK-OAK"), ("Finish: Walnut", None, 20, "LMP-DSK-WNT")],
            ),
            (
                "Face Moisturizer",
                "Beauty",
                Decimal("42.00"),
                Decimal("4.5"),
                1567,
                False,
                "Lightweight daily moisturizer with SPF 30 and niacinamide. Oil-free formula suitable for all skin types. Provides 24-hour hydration without greasiness.",
                "https://images.unsplash.com/photo-1611930022073-b7a4ba5fcccd?w=400",
                [("Size: 50ml", None, 150, "MST-FC-50"), ("Size: 100ml", Decimal("68.00"), 80, "MST-FC-100")],
            ),
            (
                "Fiction Bestseller Collection",
                "Books",
                Decimal("39.99"),
                Decimal("4.8"),
                3456,
                True,
                "Curated box set of 5 contemporary fiction bestsellers. Beautifully bound editions with exclusive author notes. Perfect gift for book lovers.",
                "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400",
                [("Edition: Paperback", None, 200, "BKS-FIC-PB"), ("Edition: Hardcover", Decimal("59.99"), 80, "BKS-FIC-HC")],
            ),
            (
                "Throw Pillow Set",
                "Furniture",
                Decimal("55.00"),
                Decimal("4.3"),
                198,
                False,
                "Set of 2 textured throw pillows in neutral tones. Premium cotton covers with hidden zippers. Hypoallergenic insert included.",
                "https://images.unsplash.com/photo-1584100936595-c0654b55a2e2?w=400",
                [("Color: Cream", None, 45, "PLW-THR-CRM"), ("Color: Charcoal", None, 40, "PLW-THR-CHR"), ("Color: Sage", None, 30, "PLW-THR-SGE")],
            ),
        ]

        for name, category, price, rating, reviews, featured, desc, image_url, variants in products_data:
            product = Product(
                id=uuid.uuid5(uuid.NAMESPACE_DNS, f"product-{name}"),
                category_id=cats[category].id,
                name=name,
                description=desc,
                base_price=price,
                avg_rating=rating,
                review_count=reviews,
                is_featured=featured,
            )
            db.add(product)

            # Primary image
            db.add(ProductImage(
                product_id=product.id,
                image_url=image_url,
                sort_order=0,
                is_primary=True,
            ))

            # Variants
            for label, price_override, stock, sku in variants:
                db.add(ProductVariant(
                    product_id=product.id,
                    variant_label=label,
                    price_override=price_override,
                    stock_quantity=stock,
                    sku=sku,
                ))

        # ── Banners (from Home screen) ─────────────────────────────
        db.add(Banner(
            title="FLASH SALE",
            subtitle="Up to 50% Off",
            cta_text="Shop Now",
            cta_link="/products?sale=true",
            image_url="https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?w=600",
            sort_order=1,
            is_active=True,
        ))
        db.add(Banner(
            title="NEW ARRIVALS",
            subtitle="Fresh styles just dropped",
            cta_text="Explore",
            cta_link="/products?sort=newest",
            image_url="https://images.unsplash.com/photo-1483985988355-763728e1935b?w=600",
            sort_order=2,
            is_active=True,
        ))
        db.add(Banner(
            title="FREE DELIVERY",
            subtitle="On orders above $50",
            cta_text="Learn More",
            cta_link="/info/delivery",
            image_url="https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=600",
            sort_order=3,
            is_active=True,
        ))

        await db.commit()
        print("Seed complete!")
        print(f"  - 1 demo user (akhil@vibeshopping.com / Password123!)")
        print(f"  - 1 address")
        print(f"  - {len(categories_data)} categories")
        print(f"  - {len(products_data)} products with variants & images")
        print(f"  - 3 banners")


if __name__ == "__main__":
    asyncio.run(seed())
