from shop.models import Category


class CategoryRepository:

    @staticmethod
    def create_category(**data):
        return Category.objects.create(**data)

    @staticmethod
    def get_category(category_id):
        return Category.objects.get(category_id=category_id)

    @staticmethod
    def get_all_categories():
        return Category.objects.all()

    @staticmethod
    def update_category(category_id, **data):
        Category.objects.filter(category_id=category_id).update(**data)
        return Category.objects.get(category_id=category_id)

    @staticmethod
    def delete_category(category_id):
        return Category.objects.filter(category_id=category_id).delete()