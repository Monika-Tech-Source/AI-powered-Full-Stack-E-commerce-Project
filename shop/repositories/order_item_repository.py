from shop.models import OrderItem


class OrderItemRepository:

    @staticmethod
    def create_order_item(**data):
        return OrderItem.objects.create(**data)

    @staticmethod
    def get_order_item(order_item_id):
        return OrderItem.objects.get(order_item_id=order_item_id)

    @staticmethod
    def get_order_items(order_id):
        return OrderItem.objects.filter(order_id=order_id)

    @staticmethod
    def update_order_item(order_item_id, **data):
        OrderItem.objects.filter(order_item_id=order_item_id).update(**data)
        return OrderItem.objects.get(order_item_id=order_item_id)

    @staticmethod
    def delete_order_item(order_item_id):
        return OrderItem.objects.filter(
            order_item_id=order_item_id
        ).delete()