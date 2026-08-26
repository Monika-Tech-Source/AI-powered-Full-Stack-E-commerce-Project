from django.db import models


class User(models.Model):

    user_id = models.AutoField(
        primary_key=True
    )

    full_name = models.CharField(
        max_length=50
    )

    email = models.EmailField(
        max_length=100,
        unique=True
    )

    is_admin = models.BooleanField(
        default=False
    )

    password = models.CharField(
        max_length=255
    )

    phone = models.CharField(
        max_length=15,
        unique=True
    )

    address_line1 = models.CharField(
        max_length=150
    )

    address_line2 = models.CharField(
        max_length=150,
        null=True,
        blank=True
    )

    city = models.CharField(
        max_length=50
    )

    state = models.CharField(
        max_length=50
    )

    pincode = models.CharField(
        max_length=10
    )

    created_at = models.DateTimeField()


    class Meta:

        db_table = 'users'
        managed = False


# =========================================
# CATEGORY
# =========================================

class Category(models.Model):

    category_id = models.AutoField(
        primary_key=True
    )

    category_name = models.CharField(
        max_length=100
    )

    description = models.TextField()


    class Meta:

        db_table = 'categories'
        managed = False


class Product(models.Model):

    product_id = models.AutoField(
        primary_key=True
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.DO_NOTHING,
        db_column='category_id'
    )

    product_type = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    product_name = models.CharField(
        max_length=150
    )

    description = models.TextField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    brand = models.CharField(
        max_length=200,
        null=True,
        blank=True
    )

    image_url = models.CharField(
        max_length=255
    )

    gender = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField()

    class Meta:

        db_table = 'products'
        managed = False

# =========================================
# PRODUCT VARIANT
# =========================================

class ProductVariant(models.Model):

    variant_id = models.AutoField(
        primary_key=True
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.DO_NOTHING,
        db_column='product_id'
    )

    size = models.CharField(
        max_length=10
    )

    stock_quantity = models.IntegerField(
        default=0
    )


    class Meta:

        db_table = 'product_variants'
        managed = False


# =========================================
# CART
# =========================================

class Cart(models.Model):

    cart_id = models.AutoField(
        primary_key=True
    )

    user = models.OneToOneField(
        User,
        on_delete=models.DO_NOTHING,
        db_column='user_id'
    )

    created_at = models.DateTimeField()


    class Meta:

        db_table = 'cart'
        managed = False


# =========================================
# CART ITEM
# =========================================

class CartItem(models.Model):

    cart_item_id = models.AutoField(
        primary_key=True
    )

    cart = models.ForeignKey(
        Cart,
        on_delete=models.DO_NOTHING,
        db_column='cart_id'
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.DO_NOTHING,
        db_column='variant_id'
    )

    quantity = models.IntegerField(
        default=1
    )


    class Meta:

        db_table = 'cart_items'
        managed = False


# =========================================
# ORDER
# =========================================

class Order(models.Model):

    order_id = models.AutoField(
        primary_key=True
    )

    user = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        db_column='user_id'
    )

    order_date = models.DateTimeField()

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_method = models.CharField(
        max_length=50
    )

    order_status = models.CharField(
        max_length=50,
        choices=[
            ('PLACED', 'PLACED'),
            ('CONFIRMED', 'CONFIRMED'),
            ('SHIPPED', 'SHIPPED'),
            ('OUT FOR DELIVERY', 'OUT FOR DELIVERY'),
            ('DELIVERED', 'DELIVERED'),
            ('CANCELLED', 'CANCELLED'),
        ],
        default='PLACED'
    )

    delivery_name = models.CharField(
        max_length=100
    )

    delivery_phone = models.CharField(
        max_length=15
    )

    delivery_address_line1 = models.CharField(
        max_length=150
    )

    delivery_address_line2 = models.CharField(
        max_length=150,
        null=True,
        blank=True
    )

    delivery_city = models.CharField(
        max_length=100
    )

    delivery_state = models.CharField(
        max_length=100
    )

    delivery_pincode = models.CharField(
        max_length=10
    )

    delivery_country = models.CharField(
        max_length=100,
        default='India'
    )


    class Meta:

        db_table = 'orders'
        managed = False


# =========================================
# ORDER ITEM
# =========================================

class OrderItem(models.Model):

    order_item_id = models.AutoField(
        primary_key=True
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.DO_NOTHING,
        db_column='order_id'
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.DO_NOTHING,
        db_column='variant_id'
    )

    quantity = models.IntegerField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )


    class Meta:

        db_table = 'order_items'
        managed = False


# =========================================
# WISHLIST
# =========================================

class Wishlist(models.Model):

    wishlist_id = models.AutoField(
        primary_key=True
    )

    user = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        db_column='user_id'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.DO_NOTHING,
        db_column='product_id'
    )

    created_at = models.DateTimeField()


    class Meta:

        db_table = 'wishlist'
        managed = False

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product'],
                name='unique_user_product_wishlist'
            )
        ]