from shop.repositories.cart_item_repository import CartItemRepository


class CartItemService:

    @staticmethod
    def create_cart_item(**data):
        return CartItemRepository.create_cart_item(**data)

    @staticmethod
    def get_cart_item(cart_item_id):
        return CartItemRepository.get_cart_item(cart_item_id)

    @staticmethod
    def get_cart_items(cart_id):
        return CartItemRepository.get_cart_items(cart_id)

    @staticmethod
    def update_cart_item(cart_item_id, **data):
        return CartItemRepository.update_cart_item(cart_item_id, **data)

    @staticmethod
    def delete_cart_item(cart_item_id):
        return CartItemRepository.delete_cart_item(cart_item_id)