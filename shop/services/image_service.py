import os
import re
from difflib import SequenceMatcher

from django.conf import settings

from ..models import Product


class ImageService:

    # =========================================================
    # MAIN PRODUCT IMAGE DIRECTORY
    # =========================================================

    @staticmethod
    def get_products_directory():

        return os.path.join(
            settings.BASE_DIR,
            'shop',
            'static',
            'shop',
            'images',
            'products'
        )

    # =========================================================
    # GET ALL PRODUCT IMAGES
    # =========================================================

    @staticmethod
    def get_all_product_images():

        images = []

        products_directory = (
            ImageService.get_products_directory()
        )

        if not os.path.exists(products_directory):
            return images

        for root, directories, files in os.walk(
            products_directory
        ):

            for file_name in files:

                if file_name.lower().endswith(
                    ('.jpg', '.jpeg', '.png', '.webp')
                ):

                    full_path = os.path.join(
                        root,
                        file_name
                    )

                    relative_path = os.path.relpath(
                        full_path,
                        os.path.join(
                            settings.BASE_DIR,
                            'shop',
                            'static'
                        )
                    )

                    # Convert Windows \ to /
                    relative_path = relative_path.replace(
                        '\\',
                        '/'
                    )

                    images.append(
                        relative_path
                    )

        return images

    # =========================================================
    # NORMALIZE TEXT
    # =========================================================

    @staticmethod
    def normalize_text(text):

        if not text:
            return ''

        text = str(text).lower()

        # Remove image extension
        text = re.sub(
            r'\.(jpg|jpeg|png|webp)$',
            '',
            text
        )

        # Replace special characters with spaces
        text = re.sub(
            r'[^a-z0-9]+',
            ' ',
            text
        )

        return text.strip()

    # =========================================================
    # GET GENDER FROM IMAGE PATH
    # =========================================================

    @staticmethod
    def get_gender_from_path(image_path):

        path = image_path.lower().replace(
            '\\',
            '/'
        )

        if 'women_products/' in path:
            return 'Women'

        if 'men_products/' in path:
            return 'Men'

        if 'kids_products/' in path:
            return 'Kids'

        # Accessories are gender-neutral
        if 'accessories/' in path:
            return None

        return None

    # =========================================================
    # GET IMAGE NAME
    # =========================================================

    @staticmethod
    def get_image_name(image_path):

        file_name = os.path.basename(
            image_path
        )

        return ImageService.normalize_text(
            file_name
        )

    # =========================================================
    # GET CATEGORY NAME
    # =========================================================

    @staticmethod
    def get_category_name(product):

        if not product.category:
            return ''

        return ImageService.normalize_text(
            product.category.category_name
        )

    # =========================================================
    # DETERMINE PRODUCT GENDER
    # =========================================================

    @staticmethod
    def get_product_gender(product):

        # -----------------------------------------------------
        # 1. USE GENDER STORED IN DATABASE
        # -----------------------------------------------------

        if hasattr(product, 'gender') and product.gender:
            return product.gender

        # -----------------------------------------------------
        # 2. CHECK CATEGORY
        # -----------------------------------------------------

        if product.category:

            category_name = (
                product.category.category_name
                .strip()
                .lower()
            )

        else:

            category_name = ''

        if category_name == 'men':
            return 'Men'

        if category_name == 'women':
            return 'Women'

        if category_name == 'kids':
            return 'Kids'

        # -----------------------------------------------------
        # 3. CHECK PRODUCT NAME
        # -----------------------------------------------------

        product_name = (
            product.product_name
            .strip()
            .lower()
        )

        if re.search(
            r'\bmen\b|\bman\b',
            product_name
        ):
            return 'Men'

        if re.search(
            r'\bwomen\b|\bwoman\b',
            product_name
        ):
            return 'Women'

        if re.search(
            r'\bkids?\b|\bboys?\b|\bgirls?\b',
            product_name
        ):
            return 'Kids'

        # -----------------------------------------------------
        # 4. UNKNOWN
        # -----------------------------------------------------

        return None

    # =========================================================
    # DETERMINE PRODUCT TYPE
    # =========================================================

    @staticmethod
    def get_product_type(product):

        if product.category:

            category_name = (
                product.category.category_name
                .strip()
                .lower()
            )

        else:

            category_name = ''

        product_name = (
            product.product_name
            .strip()
            .lower()
        )

        # =====================================================
        # ACCESSORIES / FOOTWEAR
        # =====================================================

        if 'running shoe' in product_name:
            return 'running_shoes'

        if 'casual sneaker' in product_name:
            return 'casual_sneakers'

        if 'leather belt' in product_name:
            return 'leather_belts'

        if 'classic handbag' in product_name:
            return 'classic_handbags'

        # =====================================================
        # JEANS
        # =====================================================

        if category_name == 'jeans':
            return 'jeans'

        if 'jean' in product_name:
            return 'jeans'

        # =====================================================
        # SHORTS
        # =====================================================

        if category_name == 'shorts':
            return 'shorts'

        if 'short' in product_name:
            return 'shorts'

        # =====================================================
        # DRESSES
        # =====================================================

        if category_name == 'dresses':
            return 'dresses'

        if 'dress' in product_name:
            return 'dresses'

        # =====================================================
        # TOPS
        # =====================================================

        if category_name in [
            'shirts',
            't-shirts',
            'tops'
        ]:
            return 'tops'

        if (
            'shirt' in product_name
            or 't-shirt' in product_name
            or 'tshirt' in product_name
            or 'hoodie' in product_name
            or 'sweatshirt' in product_name
            or 'top' in product_name
        ):
            return 'tops'

        return None

    # =========================================================
    # GET CORRECT FOLDER(S)
    # =========================================================

    @staticmethod
    def get_candidate_folders(product):

        gender = ImageService.get_product_gender(product)
        product_type = ImageService.get_product_type(product)

        # =====================================================
        # ACCESSORIES
        # =====================================================

        if product_type == 'running_shoes':

            return [
                'accessories/running_shoes'
            ]

        if product_type == 'casual_sneakers':

            return [
                'accessories/casual_sneakers'
            ]

        if product_type == 'leather_belts':

            return [
                'accessories/leather_belts'
            ]

        if product_type == 'classic_handbags':

            return [
                'accessories/classic_handbags'
            ]

        # =====================================================
        # MEN
        # =====================================================

        if gender == 'Men':

            if product_type == 'jeans':

                return [
                    'men_products/men_Jeans'
                ]

            if product_type == 'tops':

                return [
                    'men_products/men_shirts_Tshirts'
                ]

            return [
                'men_products/men_shirts_Tshirts',
                'men_products/men_Jeans'
            ]

        # =====================================================
        # WOMEN
        # =====================================================

        if gender == 'Women':

            if product_type == 'jeans':

                return [
                    'women_products/women_jeans'
                ]

            if product_type == 'tops':

                return [
                    'women_products/women_Tops'
                ]

            return [
                'women_products/women_Tops',
                'women_products/women_jeans'
            ]

        # =====================================================
        # KIDS
        # =====================================================

        if gender == 'Kids':

            return [
                'kids_products/boys_kids_products',
                'kids_products/girls_kids_products'
            ]

        return []

    # =========================================================
    # GET IMAGES INSIDE SPECIFIC FOLDERS
    # =========================================================

    @staticmethod
    def get_images_from_folders(
        images,
        candidate_folders
    ):

        matching_images = []

        for image_path in images:

            normalized_path = (
                image_path
                .lower()
                .replace('\\', '/')
            )

            for folder in candidate_folders:

                normalized_folder = (
                    folder
                    .lower()
                    .replace('\\', '/')
                )

                expected_path = (
                    f'products/{normalized_folder}/'
                )

                if expected_path in normalized_path:

                    matching_images.append(
                        image_path
                    )

                    break

        return matching_images

    # =========================================================
    # CALCULATE IMAGE MATCH SCORE
    # =========================================================

    @staticmethod
    def calculate_match_score(
        product_name,
        image_name
    ):

        product_text = (
            ImageService.normalize_text(
                product_name
            )
        )

        image_text = (
            ImageService.normalize_text(
                image_name
            )
        )

        if not product_text or not image_text:
            return 0

        # =====================================================
        # EXACT MATCH
        # =====================================================

        if product_text == image_text:
            return 1.0

        # =====================================================
        # REMOVE GENDER WORDS
        # =====================================================

        product_words = set(
            product_text.split()
        )

        image_words = set(
            image_text.split()
        )

        gender_words = {
            'men',
            'man',
            'women',
            'woman',
            'kids',
            'kid',
            'boys',
            'boy',
            'girls',
            'girl'
        }

        product_words_without_gender = (
            product_words - gender_words
        )

        if product_words_without_gender:

            product_words = (
                product_words_without_gender
            )

        # =====================================================
        # WORD MATCH
        # =====================================================

        common_words = (
            product_words.intersection(
                image_words
            )
        )

        word_score = (
            len(common_words)
            / len(product_words)
        )

        # =====================================================
        # STRING SIMILARITY
        # =====================================================

        similarity = SequenceMatcher(
            None,
            product_text,
            image_text
        ).ratio()

        # =====================================================
        # PARTIAL WORD MATCH
        # =====================================================

        partial_matches = 0

        for product_word in product_words:

            for image_word in image_words:

                if (
                    len(product_word) >= 4
                    and (
                        product_word in image_word
                        or image_word in product_word
                    )
                ):

                    partial_matches += 1
                    break

        partial_score = (
            partial_matches
            / len(product_words)
        )

        # =====================================================
        # RETURN BEST SCORE
        # =====================================================

        return max(
            word_score,
            similarity,
            partial_score
        )

    # =========================================================
    # FIND BEST IMAGE
    # =========================================================

    @staticmethod
    def find_best_image(
        product,
        images
    ):

        candidate_folders = (
            ImageService.get_candidate_folders(
                product
            )
        )

        # -----------------------------------------------------
        # GET IMAGES ONLY FROM CORRECT FOLDERS
        # -----------------------------------------------------

        candidate_images = (
            ImageService.get_images_from_folders(
                images,
                candidate_folders
            )
        )

        if not candidate_images:
            return None

        # -----------------------------------------------------
        # GENDER SAFETY CHECK
        # -----------------------------------------------------

        product_gender = (
            ImageService.get_product_gender(
                product
            )
        )

        filtered_images = []

        for image_path in candidate_images:

            image_gender = (
                ImageService.get_gender_from_path(
                    image_path
                )
            )

            # Accessories are gender-neutral
            if (
                image_gender is None
                and 'accessories/' in image_path.lower()
            ):

                filtered_images.append(
                    image_path
                )

                continue

            # Gender-specific images
            if image_gender == product_gender:

                filtered_images.append(
                    image_path
                )

        candidate_images = filtered_images

        if not candidate_images:
            return None

        # -----------------------------------------------------
        # FIND BEST MATCH
        # -----------------------------------------------------

        best_image = None
        best_score = 0

        for image_path in candidate_images:

            image_name = (
                ImageService.get_image_name(
                    image_path
                )
            )

            score = (
                ImageService.calculate_match_score(
                    product.product_name,
                    image_name
                )
            )

            if score > best_score:

                best_score = score
                best_image = image_path

        # -----------------------------------------------------
        # MINIMUM MATCH SCORE
        # -----------------------------------------------------

        if best_score >= 0.35:

            return best_image

        return None

    # =========================================================
    # SYNC PRODUCT IMAGES
    # =========================================================

    @staticmethod
    def sync_product_images():

        images = (
            ImageService.get_all_product_images()
        )

        products = Product.objects.all()

        updated_products = []

        for product in products:

            best_image = (
                ImageService.find_best_image(
                    product,
                    images
                )
            )

            # Do not overwrite if no valid image
            if not best_image:
                continue

            gender = (
                ImageService.get_product_gender(
                    product
                )
            )

            # -------------------------------------------------
            # UPDATE IMAGE
            # -------------------------------------------------

            product.image_url = best_image

            update_fields = [
                'image_url'
            ]

            # -------------------------------------------------
            # UPDATE GENDER
            # -------------------------------------------------

            if hasattr(product, 'gender'):

                if gender:

                    product.gender = gender

                    update_fields.append(
                        'gender'
                    )

            product.save(
                update_fields=update_fields
            )

            updated_products.append(
                (
                    product.product_id,
                    product.product_name,
                    best_image,
                    gender
                )
            )

        return updated_products