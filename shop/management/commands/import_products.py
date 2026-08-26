from pathlib import Path
from decimal import Decimal

from django.core.management.base import BaseCommand

from shop.models import (
    Product,
    ProductImage,
    ProductVariant,
    Category,
)


class Command(BaseCommand):

    help = "Import all products from the current image folder structure"

    def handle(self, *args, **kwargs):

        # =========================================================
        # PRODUCT IMAGE ROOT
        # =========================================================

        base_path = (
            Path(__file__).resolve().parents[2]
            / "static"
            / "shop"
            / "images"
            / "products"
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Scanning images from: {base_path}"
            )
        )

        # =========================================================
        # CATEGORY MAPPING
        # =========================================================

        category_mapping = {

            "men_products": 1,

            "women_products": 2,

            "kids_products": 3,

            "dresses": 4,

            "mens_womens_Tshirts": 5,

            "men_womens_shirts": 6,

            "Jeans": 7,

            "footwear": 8,

            "accessories": 9,
        }

        # =========================================================
        # DEFAULT STOCK
        # =========================================================

        default_stock = 10

        # =========================================================
        # IMAGE EXTENSIONS
        # =========================================================

        image_extensions = {
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
        }

        imported_count = 0

        skipped_count = 0

        variant_created_count = 0

        image_created_count = 0

        variant_updated_count = 0

        price_updated_count = 0

        # =========================================================
        # SCAN CATEGORY FOLDERS
        # =========================================================

        for category_folder, category_id in category_mapping.items():

            category_path = base_path / category_folder

            if not category_path.exists():

                self.stdout.write(
                    self.style.WARNING(
                        f"Folder not found: {category_path}"
                    )
                )

                continue

            # =====================================================
            # GET CATEGORY
            # =====================================================

            try:

                category = Category.objects.get(
                    category_id=category_id
                )

            except Category.DoesNotExist:

                self.stdout.write(
                    self.style.ERROR(
                        f"Category ID {category_id} not found"
                    )
                )

                continue

            # =====================================================
            # FIND ALL IMAGES
            # =====================================================

            for image_path in category_path.rglob("*"):

                if image_path.suffix.lower() not in image_extensions:

                    continue

                # =================================================
                # IMAGE URL
                # =================================================

                relative_path = image_path.relative_to(
                    base_path
                )

                image_url = (
                    "shop/images/products/"
                    + str(relative_path).replace(
                        "\\",
                        "/"
                    )
                )

                # =================================================
                # PRODUCT NAME
                # =================================================

                product_name = image_path.stem

                product_name = (
                    product_name
                    .replace("_", " ")
                    .replace("-", " ")
                )

                product_name = " ".join(
                    product_name.split()
                ).title()

                # =================================================
                # PRODUCT TYPE
                # =================================================

                product_type = self.get_product_type(
                    image_path,
                    category_folder
                )

                # =================================================
                # GENDER
                # =================================================

                gender = self.get_gender(
                    image_path,
                    category_folder
                )

                # =================================================
                # CHECK EXISTING PRODUCT
                # =================================================

                existing_product = Product.objects.filter(
                    image_url=image_url
                ).first()

                # =================================================
                # EXISTING PRODUCT
                # =================================================

                if existing_product:

                    existing_product.category_id = category_id

                    existing_product.product_type = product_type

                    existing_product.gender = gender

                    existing_product.is_active = True

                    # =================================================
                    # DIFFERENT PRICE FOR EVERY PRODUCT
                    # =================================================

                    new_price = self.get_product_price(
                        existing_product.product_id
                    )

                    if existing_product.price != new_price:

                        existing_product.price = new_price

                        existing_product.save(
                            update_fields=[
                                "category",
                                "product_type",
                                "gender",
                                "is_active",
                                "price",
                            ]
                        )

                        price_updated_count += 1

                    else:

                        existing_product.save(
                            update_fields=[
                                "category",
                                "product_type",
                                "gender",
                                "is_active",
                            ]
                        )

                    skipped_count += 1

                    self.stdout.write(
                        f"Already exists: {product_name}"
                    )

                    # =================================================
                    # ENSURE ALL PRODUCT SIZES
                    # =================================================

                    variant_created, variant_updated = (
                        self.ensure_product_variants(
                            existing_product,
                            category_id,
                            product_type,
                            default_stock
                        )
                    )

                    variant_created_count += variant_created

                    variant_updated_count += variant_updated

                    # =================================================
                    # ENSURE PRODUCT IMAGE EXISTS
                    # =================================================

                    product_image_exists = (
                        ProductImage.objects.filter(
                            product=existing_product,
                            image_url=image_url
                        ).exists()
                    )

                    if not product_image_exists:

                        ProductImage.objects.create(

                            product=existing_product,

                            image_url=image_url
                        )

                        image_created_count += 1

                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Product image created for: "
                                f"{product_name}"
                            )
                        )

                    continue

                # =================================================
                # CREATE PRODUCT
                # =================================================

                product_price = self.get_product_price_from_image(
                    image_path
                )

                product = Product.objects.create(

                    category=category,

                    product_type=product_type,

                    product_name=product_name,

                    description=(
                        f"{product_name} "
                        "designed for modern everyday style."
                    ),

                    price=product_price,

                    brand="BHAVIKA",

                    image_url=image_url,

                    gender=gender,

                    is_active=True,
                )

                imported_count += 1

                price_updated_count += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Imported: {product_name} "
                        f"| Price: ₹{product_price}"
                    )
                )

                # =================================================
                # CREATE PRODUCT IMAGE
                # =================================================

                ProductImage.objects.create(

                    product=product,

                    image_url=image_url
                )

                image_created_count += 1

                # =================================================
                # CREATE ALL PRODUCT VARIANTS
                # =================================================

                variant_created, variant_updated = (
                    self.ensure_product_variants(
                        product,
                        category_id,
                        product_type,
                        default_stock
                    )
                )

                variant_created_count += variant_created

                variant_updated_count += variant_updated

        # =========================================================
        # FINAL RESULT
        # =========================================================

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "========================================="
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported products: {imported_count}"
            )
        )

        self.stdout.write(
            f"Skipped existing products: {skipped_count}"
        )

        self.stdout.write(
            f"Prices updated: {price_updated_count}"
        )

        self.stdout.write(
            f"Variants created: {variant_created_count}"
        )

        self.stdout.write(
            f"Variants updated: {variant_updated_count}"
        )

        self.stdout.write(
            f"Product images created: {image_created_count}"
        )

        self.stdout.write(
            self.style.SUCCESS(
                "========================================="
            )
        )

    # =============================================================
    # PRODUCT PRICE
    # =============================================================

    def get_product_price(self, product_id):

        price = Decimal("699.00") + (
            Decimal(str(product_id)) * Decimal("13.00")
        )

        return price.quantize(
            Decimal("0.01")
        )

    # =============================================================
    # PRICE FOR NEW PRODUCT
    # =============================================================

    def get_product_price_from_image(self, image_path):

        parts = image_path.parts

        # Temporary unique base derived from filename.
        # Final product ID based price is applied after creation.
        filename_value = sum(
            ord(character)
            for character in image_path.stem
        )

        price = Decimal("699.00") + (
            Decimal(str(filename_value % 200)) * Decimal("13.00")
        )

        return price.quantize(
            Decimal("0.01")
        )

    # =============================================================
    # GET SIZES
    # =============================================================

    def get_sizes(
        self,
        category_id,
        product_type
    ):

        # =========================================================
        # FOOTWEAR
        # =========================================================

        if category_id == 8:

            return [
                "6",
                "7",
                "8",
                "9",
                "10",
            ]

        # =========================================================
        # ACCESSORIES
        # =========================================================

        if category_id == 9:

            return [
                "One Size",
            ]

        # =========================================================
        # KIDS
        # =========================================================

        if category_id == 3:

            return [
                "2-3Y",
                "4-5Y",
                "6-7Y",
                "8-9Y",
                "10-11Y",
                "12-13Y",
            ]

        # =========================================================
        # MEN / WOMEN / DRESSES / T-SHIRTS / SHIRTS / JEANS
        # =========================================================

        return [
            "XS",
            "S",
            "M",
            "L",
            "XL",
            "XXL",
        ]

    # =============================================================
    # ENSURE ALL VARIANTS
    # =============================================================

    def ensure_product_variants(
        self,
        product,
        category_id,
        product_type,
        default_stock
    ):

        sizes = self.get_sizes(
            category_id,
            product_type
        )

        variant_created = 0

        variant_updated = 0

        existing_variants = list(
            ProductVariant.objects.filter(
                product=product
            ).order_by(
                "variant_id"
            )
        )

        # =========================================================
        # NO EXISTING VARIANT
        # =========================================================

        if not existing_variants:

            for size in sizes:

                ProductVariant.objects.create(

                    product=product,

                    size=size,

                    stock_quantity=default_stock
                )

                variant_created += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Variant created: "
                        f"{product.product_name} | "
                        f"Size: {size} | "
                        f"Stock: {default_stock}"
                    )
                )

            return variant_created, variant_updated

        # =========================================================
        # EXISTING VARIANTS
        # =========================================================

        existing_by_size = {
            variant.size: variant
            for variant in existing_variants
        }

        # =========================================================
        # KEEP EXISTING M VARIANT
        # =========================================================
        #
        # For footwear, the old M variant becomes size 8.
        #
        # For accessories, the old M variant becomes One Size.
        #
        # For clothing, M remains M.
        #
        # This avoids unnecessarily deleting an existing variant.
        # =========================================================

        if category_id == 8:

            old_m_variant = existing_by_size.get("M")

            if old_m_variant:

                old_m_variant.size = "8"

                old_m_variant.save(
                    update_fields=["size"]
                )

                existing_by_size["8"] = old_m_variant

                del existing_by_size["M"]

                variant_updated += 1

        elif category_id == 9:

            old_m_variant = existing_by_size.get("M")

            if old_m_variant:

                old_m_variant.size = "One Size"

                old_m_variant.save(
                    update_fields=["size"]
                )

                existing_by_size["One Size"] = old_m_variant

                del existing_by_size["M"]

                variant_updated += 1

        # =========================================================
        # CREATE MISSING SIZES
        # =========================================================

        for size in sizes:

            if size in existing_by_size:

                continue

            ProductVariant.objects.create(

                product=product,

                size=size,

                stock_quantity=default_stock
            )

            variant_created += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Variant created: "
                    f"{product.product_name} | "
                    f"Size: {size} | "
                    f"Stock: {default_stock}"
                )
            )

        return variant_created, variant_updated

    # =============================================================
    # PRODUCT TYPE
    # =============================================================

    def get_product_type(
        self,
        image_path,
        category_folder
    ):

        parts = [
            part.lower()
            for part in image_path.parts
        ]

        # =========================================================
        # DRESSES
        # =========================================================

        if category_folder == "dresses":

            if "mens_dresses" in parts:

                return "mens_dresses"

            if "womens_dresses" in parts:

                return "womens_dresses"

            return "dresses"

        # =========================================================
        # T-SHIRTS
        # =========================================================

        if category_folder == "mens_womens_Tshirts":

            if "mens_related_tshirts" in parts:

                return "mens_tshirts"

            if "woman_related_tshirts" in parts:

                return "womens_tshirts"

            if "women_related_tshirts" in parts:

                return "womens_tshirts"

            return "tshirts"

        # =========================================================
        # SHIRTS
        # =========================================================

        if category_folder == "men_womens_shirts":

            if "mens_related_shirts" in parts:

                return "mens_shirts"

            if "womens_related_shirts" in parts:

                return "womens_shirts"

            return "shirts"

        # =========================================================
        # JEANS
        # =========================================================

        if category_folder == "Jeans":

            if "mens_related" in parts:

                return "mens_jeans"

            if "womens_related" in parts:

                return "womens_jeans"

            return "jeans"

        # =========================================================
        # FOOTWEAR
        # =========================================================

        if category_folder == "footwear":

            if any(
                "casual_sneaker" in part
                for part in parts
            ):

                return "casual_sneakers"

            if any(
                "running_shoe" in part
                for part in parts
            ):

                return "running_shoes"

            if any(
                "sandals" in part
                for part in parts
            ):

                return "sandals"

            if any(
                "flats" in part
                for part in parts
            ):

                return "flats"

            if any(
                "heels" in part
                for part in parts
            ):

                return "heels"

            if any(
                "formal_shoe" in part
                for part in parts
            ):

                return "formal_shoes"

            return "footwear"

        # =========================================================
        # ACCESSORIES
        # =========================================================

        if category_folder == "accessories":

            if "classic_handbags" in parts:

                return "classic_handbags"

            if "mens_accessories" in parts:

                return "mens_accessories"

            if "womens_accessories" in parts:

                return "womens_accessories"

            if "mens_womens_leather_belts" in parts:

                return "leather_belts"

            return "accessories"

        # =========================================================
        # OLD MEN / WOMEN / KIDS
        # =========================================================

        if category_folder == "men_products":

            if "men_jeans" in parts:

                return "men_jeans"

            if "men_shirts_tshirts" in parts:

                return "men_shirts_tshirts"

            return "men_products"

        if category_folder == "women_products":

            if "women_jeans" in parts:

                return "women_jeans"

            if "women_tops" in parts:

                return "women_tops"

            return "women_products"

        if category_folder == "kids_products":

            if "boys_kids_products" in parts:

                return "boys"

            if "girls_kids_products" in parts:

                return "girls"

            return "kids_products"

        return category_folder

    # =============================================================
    # GENDER
    # =============================================================

    def get_gender(
        self,
        image_path,
        category_folder
    ):

        parts = [
            part.lower()
            for part in image_path.parts
        ]

        # =========================================================
        # KIDS
        # =========================================================

        if category_folder == "kids_products":

            if (
                "boys_kids_products" in parts
                or "girls_kids_products" in parts
            ):

                return "Kids"

        # =========================================================
        # MEN
        # =========================================================

        if any(
            part.startswith("mens_")
            or part.startswith("men_")
            or part == "mens"
            or part == "men"
            for part in parts
        ):

            return "Men"

        if category_folder == "men_products":

            return "Men"

        # =========================================================
        # WOMEN
        # =========================================================

        if any(
            part.startswith("womens_")
            or part.startswith("women_")
            or part == "womens"
            or part == "women"
            or part == "woman"
            for part in parts
        ):

            return "Women"

        if category_folder == "women_products":

            return "Women"

        # =========================================================
        # KIDS FALLBACK
        # =========================================================

        if category_folder == "kids_products":

            return "Kids"

        return None