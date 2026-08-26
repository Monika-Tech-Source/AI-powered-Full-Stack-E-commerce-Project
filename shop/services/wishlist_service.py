from django.utils import timezone

from ..models import Wishlist


class WishlistService:

    # =========================================
    # GET ALL WISHLIST ITEMS FOR USER
    # =========================================

    @staticmethod
    def get_wishlist_by_user(user_id):

        return Wishlist.objects.filter(
            user_id=user_id
        )


    # =========================================
    # CHECK WHETHER PRODUCT IS IN WISHLIST
    # =========================================

    @staticmethod
    def is_in_wishlist(user_id, product_id):

        return Wishlist.objects.filter(
            user_id=user_id,
            product_id=product_id
        ).exists()


    # =========================================
    # ADD PRODUCT TO WISHLIST
    # =========================================

    @staticmethod
    def add_to_wishlist(user_id, product_id):

        if not WishlistService.is_in_wishlist(
            user_id,
            product_id
        ):

            return Wishlist.objects.create(
                user_id=user_id,
                product_id=product_id,
                created_at=timezone.now()
            )

        return None


    # =========================================
    # REMOVE PRODUCT FROM WISHLIST
    # =========================================

    @staticmethod
    def remove_from_wishlist(user_id, product_id):

        Wishlist.objects.filter(
            user_id=user_id,
            product_id=product_id
        ).delete()


    # =========================================
    # TOGGLE WISHLIST
    # =========================================

    @staticmethod
    def toggle_wishlist(user_id, product_id):

        if WishlistService.is_in_wishlist(
            user_id,
            product_id
        ):

            WishlistService.remove_from_wishlist(
                user_id,
                product_id
            )

            return False

        else:

            WishlistService.add_to_wishlist(
                user_id,
                product_id
            )

            return True