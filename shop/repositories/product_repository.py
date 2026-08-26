from shop.models import Product


class ProductRepository:

    @staticmethod
    def create_product(**data):
        return Product.objects.create(**data)

    @staticmethod
    def get_product(product_id):
        return Product.objects.get(
            product_id=product_id
        )

    @staticmethod
    def get_all_products():
        return Product.objects.all()

    @staticmethod
    def get_products_by_category(category_id):
        return Product.objects.filter(
            category_id=category_id
        )

    @staticmethod
    def update_product(product_id, **data):
        Product.objects.filter(
            product_id=product_id
        ).update(**data)

        return Product.objects.get(
            product_id=product_id
        )

    @staticmethod
    def delete_product(product_id):
        return Product.objects.filter(
            product_id=product_id
        ).delete()