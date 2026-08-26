from shop.models import ProductVariant


class ProductVariantRepository:

    @staticmethod
    def create_variant(**data):
        return ProductVariant.objects.create(**data)

    @staticmethod
    def get_variant(variant_id):
        return ProductVariant.objects.get(variant_id=variant_id)

    @staticmethod
    def get_variants_by_product(product_id):
        return ProductVariant.objects.filter(product_id=product_id)

    @staticmethod
    def get_all_variants():
        return ProductVariant.objects.all()

    @staticmethod
    def update_variant(variant_id, **data):
        ProductVariant.objects.filter(variant_id=variant_id).update(**data)
        return ProductVariant.objects.get(variant_id=variant_id)

    @staticmethod
    def delete_variant(variant_id):
        return ProductVariant.objects.filter(variant_id=variant_id).delete()