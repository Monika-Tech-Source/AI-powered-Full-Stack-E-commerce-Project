from shop.repositories.order_item_repository import OrderItemRepository


class OrderItemService:

    @staticmethod
    def create_order_item(**data):
        return OrderItemRepository.create_order_item(**data)

    @staticmethod
    def get_order_item(order_item_id):
        return OrderItemRepository.get_order_item(order_item_id)

    @staticmethod
    def get_order_items(order_id):
        return OrderItemRepository.get_order_items(order_id)

    @staticmethod
    def update_order_item(order_item_id, **data):
        return OrderItemRepository.update_order_item(
            order_item_id,
            **data
        )

    @staticmethod
    def delete_order_item(order_item_id):
        return OrderItemRepository.delete_order_item(order_item_id)