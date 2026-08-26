from shop.repositories.product_variant_repository import ProductVariantRepository


class ProductVariantService:

    @staticmethod
    def create_variant(**data):
        return ProductVariantRepository.create_variant(**data)

    @staticmethod
    def get_variant(variant_id):
        return ProductVariantRepository.get_variant(variant_id)

    @staticmethod
    def get_variants_by_product(product_id):
        return ProductVariantRepository.get_variants_by_product(product_id)

    @staticmethod
    def get_all_variants():
        return ProductVariantRepository.get_all_variants()

    @staticmethod
    def update_variant(variant_id, **data):
        return ProductVariantRepository.update_variant(variant_id, **data)

    @staticmethod
    def delete_variant(variant_id):
        return ProductVariantRepository.delete_variant(variant_id)