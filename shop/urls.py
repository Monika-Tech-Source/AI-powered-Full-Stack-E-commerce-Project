from django.urls import path

from . import views


urlpatterns = [

    # =========================================
    # HOME
    # =========================================

    path(
        "",
        views.home,
        name="home"
    ),


    # =========================================
    # CATEGORY
    # =========================================

    path(
        "category/<int:category_id>/",
        views.category_products,
        name="category_products"
    ),


    # =========================================
    # PRODUCT
    # =========================================

    path(
        "product/<int:product_id>/",
        views.product_detail,
        name="product_detail"
    ),


    # =========================================
    # CART
    # =========================================

    path(
        "cart/",
        views.cart,
        name="cart"
    ),


    # =========================================
    # CHECKOUT
    # =========================================

    path(
        "checkout/",
        views.checkout,
        name="checkout"
    ),

    path(
        "order-success/",
        views.order_success,
        name="order_success"
    ),


    # =========================================
    # ORDERS
    # =========================================

    path(
        "my-orders/",
        views.my_orders,
        name="my_orders"
    ),

    path(
        "order/<int:order_id>/",
        views.order_detail,
        name="order_detail"
    ),

    path(
        "order/<int:order_id>/cancel/",
        views.cancel_order,
        name="cancel_order"
    ),


    # =========================================
    # WISHLIST
    # =========================================

    path(
        "wishlist/",
        views.wishlist,
        name="wishlist"
    ),

    path(
        "wishlist/toggle/<int:product_id>/",
        views.toggle_wishlist,
        name="toggle_wishlist"
    ),


    # =========================================
    # SEARCH
    # =========================================

    path(
        "search/",
        views.search_products,
        name="search_products"
    ),


    # =========================================
    # AUTHENTICATION
    # =========================================

    path(
        "register/",
        views.register,
        name="register"
    ),

    path(
        "login/",
        views.login_view,
        name="login"
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),


    # =========================================
    # USER PROFILE
    # =========================================

    path(
        "profile/",
        views.profile,
        name="profile"
    ),


    # =========================================
    # ADMIN DASHBOARD
    # =========================================

    path(
        "manage/",
        views.admin_dashboard,
        name="admin_dashboard"
    ),


    # =========================================
    # ADMIN ORDERS
    # =========================================

    path(
        "manage/orders/",
        views.admin_orders,
        name="admin_orders"
    ),

    path(
        "manage/orders/<int:order_id>/status/",
        views.admin_update_order_status,
        name="admin_update_order_status"
    ),


    # =========================================
    # ADMIN PRODUCTS
    # =========================================

    path(
        "manage/products/",
        views.admin_products,
        name="admin_products"
    ),

    path(
        "manage/products/add/",
        views.admin_add_product,
        name="admin_add_product"
    ),

    path(
        "manage/products/<int:product_id>/edit/",
        views.admin_edit_product,
        name="admin_edit_product"
    ),

    path(
        "manage/products/<int:product_id>/toggle/",
        views.admin_toggle_product,
        name="admin_toggle_product"
    ),


    # =========================================
    # ADMIN STOCK
    # =========================================

    path(
        "manage/products/variant/<int:variant_id>/stock/",
        views.admin_update_stock,
        name="admin_update_stock"
    ),
]