from shop.models import CartItem


class CartItemRepository:

    @staticmethod
    def create_cart_item(**data):
        return CartItem.objects.create(**data)

    @staticmethod
    def get_cart_item(cart_item_id):
        return CartItem.objects.get(cart_item_id=cart_item_id)

    @staticmethod
    def get_cart_items(cart_id):
        return CartItem.objects.filter(cart_id=cart_id)

    @staticmethod
    def update_cart_item(cart_item_id, **data):
        CartItem.objects.filter(cart_item_id=cart_item_id).update(**data)
        return CartItem.objects.get(cart_item_id=cart_item_id)

    @staticmethod
    def delete_cart_item(cart_item_id):
        return CartItem.objects.filter(cart_item_id=cart_item_id).delete()