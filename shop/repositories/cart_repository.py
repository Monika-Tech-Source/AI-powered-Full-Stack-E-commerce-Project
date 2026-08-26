from shop.models import Cart


class CartRepository:

    @staticmethod
    def create_cart(**data):
        return Cart.objects.create(**data)

    @staticmethod
    def get_cart(cart_id):
        return Cart.objects.get(cart_id=cart_id)

    @staticmethod
    def get_cart_by_user(user_id):
        return Cart.objects.get(user_id=user_id)

    @staticmethod
    def get_all_carts():
        return Cart.objects.all()

    @staticmethod
    def delete_cart(cart_id):
        return Cart.objects.filter(cart_id=cart_id).delete()