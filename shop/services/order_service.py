from shop.repositories.order_repository import OrderRepository


class OrderService:

    @staticmethod
    def create_order(**data):
        return OrderRepository.create_order(**data)

    @staticmethod
    def get_order(order_id):
        return OrderRepository.get_order(order_id)

    @staticmethod
    def get_orders_by_user(user_id):
        return OrderRepository.get_orders_by_user(user_id)

    @staticmethod
    def get_all_orders():
        return OrderRepository.get_all_orders()

    @staticmethod
    def update_order(order_id, **data):
        return OrderRepository.update_order(order_id, **data)

    @staticmethod
    def delete_order(order_id):
        return OrderRepository.delete_order(order_id)