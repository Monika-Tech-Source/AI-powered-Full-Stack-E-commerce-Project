from shop.models import Order


class OrderRepository:

    @staticmethod
    def create_order(**data):
        return Order.objects.create(**data)

    @staticmethod
    def get_order(order_id):
        return Order.objects.get(order_id=order_id)

    @staticmethod
    def get_orders_by_user(user_id):
        return Order.objects.filter(user_id=user_id)

    @staticmethod
    def get_all_orders():
        return Order.objects.all()

    @staticmethod
    def update_order(order_id, **data):
        Order.objects.filter(order_id=order_id).update(**data)
        return Order.objects.get(order_id=order_id)

    @staticmethod
    def delete_order(order_id):
        return Order.objects.filter(order_id=order_id).delete()