from shop.repositories.cart_repository import CartRepository


class CartService:

    @staticmethod
    def create_cart(**data):
        return CartRepository.create_cart(**data)

    @staticmethod
    def get_cart(cart_id):
        return CartRepository.get_cart(cart_id)

    @staticmethod
    def get_cart_by_user(user_id):
        return CartRepository.get_cart_by_user(user_id)

    @staticmethod
    def get_all_carts():
        return CartRepository.get_all_carts()

    @staticmethod
    def delete_cart(cart_id):
        return CartRepository.delete_cart(cart_id)