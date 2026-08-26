from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.db.models import Q

from .models import (
    User,
    Product,
    ProductVariant,
    Category,
    Order,
)

from .services.category_service import CategoryService
from .services.product_service import ProductService
from .services.product_variant_service import ProductVariantService
from .services.cart_service import CartService
from .services.cart_item_service import CartItemService
from .services.order_service import OrderService
from .services.order_item_service import OrderItemService
from .services.wishlist_service import WishlistService
from .services.user_service import UserService


# =========================================
# COMMON HELPERS
# =========================================

def get_logged_in_user_id(request):

    return request.session.get("user_id")


def get_admin_user(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return None

    try:

        user = UserService.get_user(user_id)

    except Exception:

        return None

    if not user:
        return None

    if not user.is_admin:
        return None

    return user


# =========================================
# HOME PAGE
# =========================================

def home(request):

    categories = CategoryService.get_all_categories()

    products = ProductService.get_all_products().filter(
        is_active=True
    ).order_by(
        "-product_id"
    )[:12]

    return render(
        request,
        "shop/home.html",
        {
            "categories": categories,
            "products": products,
        }
    )


# =========================================
# CATEGORY PRODUCTS
# =========================================

def category_products(request, category_id):

    # =========================================
    # GET CATEGORY
    # =========================================

    try:

        category = CategoryService.get_category(
            category_id
        )

    except Exception:

        messages.error(
            request,
            "Category not found."
        )

        return redirect("home")

    if not category:

        messages.error(
            request,
            "Category not found."
        )

        return redirect("home")

    # =========================================
    # GET ACTIVE PRODUCTS
    # =========================================

    products = ProductService.get_all_products().filter(
        is_active=True
    )

    # =========================================
    # CATEGORY FILTER
    # =========================================

    if category.category_name == "Men":

        products = products.filter(
            category_id=1
        )

    elif category.category_name == "Women":

        products = products.filter(
            category_id=2
        )

    elif category.category_name == "Kids":

        products = products.filter(
            category_id=3
        )

    else:

        products = products.filter(
            category_id=category_id
        )

    # =========================================
    # PRODUCT TYPE FILTER
    # =========================================

    product_type = request.GET.get(
        "product_type",
        ""
    ).strip()

    if product_type:

        products = products.filter(
            product_type=product_type
        )

    # =========================================
    # GENDER FILTER
    # =========================================

    gender = request.GET.get(
        "gender",
        ""
    ).strip()

    if gender:

        products = products.filter(
            gender=gender
        )

    # =========================================
    # MINIMUM PRICE FILTER
    # =========================================

    min_price = request.GET.get(
        "min_price",
        ""
    ).strip()

    if min_price:

        try:

            products = products.filter(
                price__gte=float(min_price)
            )

        except ValueError:

            min_price = ""

    # =========================================
    # MAXIMUM PRICE FILTER
    # =========================================

    max_price = request.GET.get(
        "max_price",
        ""
    ).strip()

    if max_price:

        try:

            products = products.filter(
                price__lte=float(max_price)
            )

        except ValueError:

            max_price = ""

    # =========================================
    # SORTING
    # =========================================

    sort = request.GET.get(
        "sort",
        ""
    ).strip()

    if sort == "price_low":

        products = products.order_by(
            "price"
        )

    elif sort == "price_high":

        products = products.order_by(
            "-price"
        )

    elif sort == "name_az":

        products = products.order_by(
            "product_name"
        )

    elif sort == "name_za":

        products = products.order_by(
            "-product_name"
        )

    elif sort == "newest":

        products = products.order_by(
            "-created_at"
        )

    else:

        products = products.order_by(
            "-product_id"
        )

    # =========================================
    # FILTER OPTIONS
    # =========================================

    product_types = ProductService.get_all_products().filter(
        is_active=True
    ).values_list(
        "product_type",
        flat=True
    ).distinct()

    genders = ProductService.get_all_products().filter(
        is_active=True
    ).values_list(
        "gender",
        flat=True
    ).distinct()

    # =========================================
    # DISPLAY CATEGORY PAGE
    # =========================================

    return render(
        request,
        "shop/category.html",
        {
            "category": category,
            "products": products,

            "selected_product_type": product_type,
            "selected_gender": gender,

            "min_price": min_price,
            "max_price": max_price,

            "selected_sort": sort,

            "product_types": product_types,
            "genders": genders,
        }
    )


# =========================================
# SEARCH PRODUCTS
# =========================================

def search_products(request):

    query = request.GET.get(
        "q",
        ""
    ).strip()

    products = ProductService.get_all_products().filter(
        is_active=True
    )

    if query:

        products = products.filter(
            Q(product_name__icontains=query)
            | Q(brand__icontains=query)
            | Q(description__icontains=query)
            | Q(product_type__icontains=query)
            | Q(gender__icontains=query)
        )

    return render(
        request,
        "shop/search_results.html",
        {
            "products": products,
            "query": query,
        }
    )


# =========================================
# PRODUCT DETAIL PAGE
# =========================================

def product_detail(request, product_id):

    product = ProductService.get_product(
        product_id
    )

    # =========================================
    # DO NOT DISPLAY INACTIVE PRODUCTS
    # =========================================

    if not product or not product.is_active:

        messages.error(
            request,
            "This product is currently unavailable."
        )

        return redirect("home")

    # =========================================
    # GET PRODUCT VARIANTS
    # =========================================

    variants = ProductVariantService.get_variants_by_product(
        product_id
    )

    user_id = get_logged_in_user_id(request)

    # =========================================
    # CHECK WISHLIST STATUS
    # =========================================

    is_in_wishlist = False

    if user_id:

        is_in_wishlist = WishlistService.is_in_wishlist(
            user_id,
            product_id
        )

    # =========================================
    # ADD TO CART
    # =========================================

    if request.method == "POST":

        if not user_id:

            return redirect("login")

        variant_id = request.POST.get(
            "variant_id"
        )

        if variant_id:

            try:

                variant = ProductVariantService.get_variant(
                    variant_id
                )

            except Exception:

                messages.error(
                    request,
                    "Product variant not found."
                )

                return redirect(
                    "product_detail",
                    product_id=product_id
                )

            # =========================================
            # CHECK VARIANT BELONGS TO PRODUCT
            # =========================================

            if variant.product_id != product_id:

                messages.error(
                    request,
                    "Invalid product variant."
                )

                return redirect(
                    "product_detail",
                    product_id=product_id
                )

            # =========================================
            # CHECK STOCK
            # =========================================

            if variant.stock_quantity <= 0:

                messages.error(
                    request,
                    "This size is currently out of stock."
                )

                return redirect(
                    "product_detail",
                    product_id=product_id
                )

            # =========================================
            # GET CART OR CREATE CART
            # =========================================

            try:

                cart = CartService.get_cart_by_user(
                    user_id
                )

            except Exception:

                cart = CartService.create_cart(
                    user_id=user_id
                )

            # =========================================
            # GET CART ITEMS
            # =========================================

            cart_items = CartItemService.get_cart_items(
                cart.cart_id
            )

            existing_item = None

            for item in cart_items:

                if item.variant_id == variant.variant_id:

                    existing_item = item

                    break

            # =========================================
            # EXISTING CART ITEM
            # =========================================

            if existing_item:

                if (
                    existing_item.quantity
                    < variant.stock_quantity
                ):

                    CartItemService.update_cart_item(
                        existing_item.cart_item_id,
                        quantity=existing_item.quantity + 1
                    )

                    messages.success(
                        request,
                        "Product quantity increased."
                    )

                else:

                    messages.warning(
                        request,
                        "You cannot add more than the available stock."
                    )

            # =========================================
            # NEW CART ITEM
            # =========================================

            else:

                CartItemService.create_cart_item(
                    cart_id=cart.cart_id,
                    variant_id=variant.variant_id,
                    quantity=1
                )

                messages.success(
                    request,
                    "Product added to cart."
                )

            return redirect("cart")

    # =========================================
    # DISPLAY PRODUCT DETAIL
    # =========================================

    return render(
    request,
    "shop/product_detail.html",
    {
        "product": product,
        "variants": variants,
        "is_in_wishlist": is_in_wishlist,
    }
)


# =========================================
# CART PAGE
# =========================================

def cart(request):

    user_id = get_logged_in_user_id(request)

    if not user_id:

        return redirect("login")

    # =========================================
    # GET USER CART
    # =========================================

    try:

        cart = CartService.get_cart_by_user(
            user_id
        )

        cart_items = CartItemService.get_cart_items(
            cart.cart_id
        )

    except Exception:

        cart = None
        cart_items = []

    # =========================================
    # HANDLE QUANTITY CHANGES
    # =========================================

    if request.method == "POST" and cart:

        cart_item_id = request.POST.get(
            "cart_item_id"
        )

        action = request.POST.get(
            "action"
        )

        if cart_item_id and action:

            try:

                cart_item = CartItemService.get_cart_item(
                    cart_item_id
                )

            except Exception:

                return redirect("cart")

            # =========================================
            # SECURITY CHECK
            # =========================================

            if cart_item.cart_id != cart.cart_id:

                return redirect("cart")

            # =========================================
            # INCREASE
            # =========================================

            if action == "increase":

                if (
                    cart_item.quantity
                    < cart_item.variant.stock_quantity
                ):

                    CartItemService.update_cart_item(
                        cart_item.cart_item_id,
                        quantity=cart_item.quantity + 1
                    )

            # =========================================
            # DECREASE
            # =========================================

            elif action == "decrease":

                if cart_item.quantity > 1:

                    CartItemService.update_cart_item(
                        cart_item.cart_item_id,
                        quantity=cart_item.quantity - 1
                    )

                else:

                    CartItemService.delete_cart_item(
                        cart_item.cart_item_id
                    )

            # =========================================
            # REMOVE
            # =========================================

            elif action == "remove":

                CartItemService.delete_cart_item(
                    cart_item.cart_item_id
                )

        return redirect("cart")

    # =========================================
    # CALCULATE TOTAL
    # =========================================

    total = 0

    for item in cart_items:

        item.subtotal = (
            item.variant.product.price
            * item.quantity
        )

        total += item.subtotal

        # =========================================
        # STOCK STATUS
        # =========================================

        if item.variant.stock_quantity <= 0:

            item.stock_status = "OUT_OF_STOCK"

        elif item.quantity > item.variant.stock_quantity:

            item.stock_status = "INSUFFICIENT_STOCK"

        elif item.variant.stock_quantity <= 3:

            item.stock_status = "LOW_STOCK"

        else:

            item.stock_status = "AVAILABLE"

    # =========================================
    # CHECKOUT ALLOWED
    # =========================================

    can_checkout = True

    for item in cart_items:

        if (
            item.variant.stock_quantity <= 0
            or item.quantity > item.variant.stock_quantity
        ):

            can_checkout = False

            break

    # =========================================
    # DISPLAY CART
    # =========================================

    return render(
        request,
        "shop/cart.html",
        {
            "cart": cart,
            "cart_items": cart_items,
            "total": total,
            "can_checkout": can_checkout,
        }
    )


# =========================================
# CHECKOUT PAGE
# =========================================

def checkout(request):

    user_id = get_logged_in_user_id(request)

    if not user_id:

        return redirect("login")

    # =========================================
    # GET USER CART
    # =========================================

    try:

        cart = CartService.get_cart_by_user(
            user_id
        )

        cart_items = CartItemService.get_cart_items(
            cart.cart_id
        )

    except Exception:

        cart = None
        cart_items = []

    # =========================================
    # CART EMPTY
    # =========================================

    if not cart or not cart_items:

        messages.warning(
            request,
            "Your cart is empty."
        )

        return redirect("/cart/")

    # =========================================
    # CALCULATE TOTAL
    # =========================================

    total = 0

    for item in cart_items:

        item.subtotal = (
            item.variant.product.price
            * item.quantity
        )

        total += item.subtotal

    # =========================================
    # PLACE ORDER
    # =========================================

    if request.method == "POST":

        # =========================================
        # CHECK STOCK
        # =========================================

        for item in cart_items:

            if item.variant.stock_quantity <= 0:

                messages.error(
                    request,
                    f"{item.variant.product.product_name} "
                    f"is out of stock."
                )

                return redirect("/cart/")

            if item.quantity > item.variant.stock_quantity:

                messages.error(
                    request,
                    f"Only {item.variant.stock_quantity} units of "
                    f"{item.variant.product.product_name} are available."
                )

                return redirect("/cart/")

        # =========================================
        # DELIVERY DETAILS
        # =========================================

        delivery_name = request.POST.get(
            "delivery_name",
            ""
        ).strip()

        delivery_phone = request.POST.get(
            "delivery_phone",
            ""
        ).strip()

        delivery_address_line1 = request.POST.get(
            "delivery_address_line1",
            ""
        ).strip()

        delivery_address_line2 = request.POST.get(
            "delivery_address_line2",
            ""
        ).strip()

        delivery_city = request.POST.get(
            "delivery_city",
            ""
        ).strip()

        delivery_state = request.POST.get(
            "delivery_state",
            ""
        ).strip()

        delivery_pincode = request.POST.get(
            "delivery_pincode",
            ""
        ).strip()

        delivery_country = request.POST.get(
            "delivery_country",
            ""
        ).strip()

        # =========================================
        # PAYMENT METHOD
        # =========================================

        payment_method = request.POST.get(
            "payment_method",
            ""
        ).strip()

        # =========================================
        # VALIDATE NAME
        # =========================================

        if not delivery_name:

            messages.error(
                request,
                "Please enter your name."
            )

            return redirect("/checkout/")

        # =========================================
        # VALIDATE PHONE
        # =========================================

        if not delivery_phone:

            messages.error(
                request,
                "Please enter your phone number."
            )

            return redirect("/checkout/")

        if (
            not delivery_phone.isdigit()
            or len(delivery_phone) != 10
        ):

            messages.error(
                request,
                "Please enter a valid 10-digit phone number."
            )

            return redirect("/checkout/")

        # =========================================
        # VALIDATE ADDRESS
        # =========================================

        if not delivery_address_line1:

            messages.error(
                request,
                "Please enter your address."
            )

            return redirect("/checkout/")

        # =========================================
        # VALIDATE CITY
        # =========================================

        if not delivery_city:

            messages.error(
                request,
                "Please enter your city."
            )

            return redirect("/checkout/")

        # =========================================
        # VALIDATE STATE
        # =========================================

        if not delivery_state:

            messages.error(
                request,
                "Please enter your state."
            )

            return redirect("/checkout/")

        # =========================================
        # VALIDATE PINCODE
        # =========================================

        if not delivery_pincode:

            messages.error(
                request,
                "Please enter your pincode."
            )

            return redirect("/checkout/")

        if (
            not delivery_pincode.isdigit()
            or len(delivery_pincode) != 6
        ):

            messages.error(
                request,
                "Please enter a valid 6-digit pincode."
            )

            return redirect("/checkout/")

        # =========================================
        # VALIDATE COUNTRY
        # =========================================

        if not delivery_country:

            messages.error(
                request,
                "Please enter your country."
            )

            return redirect("/checkout/")

        # =========================================
        # VALIDATE PAYMENT METHOD
        # =========================================

        valid_payment_methods = [
            "Cash on Delivery",
            "UPI",
            "Card",
        ]

        if payment_method not in valid_payment_methods:

            messages.error(
                request,
                "Please select a valid payment method."
            )

            return redirect("/checkout/")

        # =========================================
        # CREATE ORDER
        # =========================================

        try:

            with transaction.atomic():

                # =========================================
                # FINAL STOCK CHECK
                # =========================================

                for item in cart_items:

                    if item.variant.stock_quantity <= 0:

                        raise ValueError(
                            f"{item.variant.product.product_name} "
                            f"is out of stock."
                        )

                    if item.quantity > item.variant.stock_quantity:

                        raise ValueError(
                            f"Not enough stock available for "
                            f"{item.variant.product.product_name}."
                        )

                # =========================================
                # CREATE ORDER
                # =========================================

                order = OrderService.create_order(

                    user_id=user_id,

                    order_date=timezone.now(),

                    total_amount=total,

                    payment_method=payment_method,

                    order_status="PLACED",

                    delivery_name=delivery_name,

                    delivery_phone=delivery_phone,

                    delivery_address_line1=delivery_address_line1,

                    delivery_address_line2=delivery_address_line2,

                    delivery_city=delivery_city,

                    delivery_state=delivery_state,

                    delivery_pincode=delivery_pincode,

                    delivery_country=delivery_country,
                )

                # =========================================
                # CREATE ORDER ITEMS
                # =========================================

                for item in cart_items:

                    OrderItemService.create_order_item(

                        order_id=order.order_id,

                        variant_id=item.variant.variant_id,

                        quantity=item.quantity,

                        price=item.variant.product.price,
                    )

                # =========================================
                # REDUCE STOCK
                # =========================================

                for item in cart_items:

                    new_stock = (
                        item.variant.stock_quantity
                        - item.quantity
                    )

                    ProductVariantService.update_variant(

                        item.variant.variant_id,

                        stock_quantity=new_stock
                    )

                # =========================================
                # CLEAR CART
                # =========================================

                for item in cart_items:

                    CartItemService.delete_cart_item(
                        item.cart_item_id
                    )

        except ValueError as error:

            messages.error(
                request,
                str(error)
            )

            return redirect("/cart/")

        except Exception:

            messages.error(
                request,
                "Unable to place your order. Please try again."
            )

            return redirect("/checkout/")

        # =========================================
        # ORDER SUCCESS
        # =========================================

        messages.success(
            request,
            "Your order has been placed successfully."
        )

        return redirect("/order-success/")

    # =========================================
    # DISPLAY CHECKOUT
    # =========================================

    return render(
        request,
        "shop/checkout.html",
        {
            "cart": cart,
            "cart_items": cart_items,
            "total": total,
        }
    )


# =========================================
# ORDER SUCCESS PAGE
# =========================================

def order_success(request):

    return render(
        request,
        "shop/order_success.html"
    )


# =========================================
# MY ORDERS PAGE
# =========================================

def my_orders(request):

    user_id = get_logged_in_user_id(request)

    if not user_id:

        return redirect("login")

    orders = OrderService.get_orders_by_user(
        user_id
    )

    return render(
        request,
        "shop/my_orders.html",
        {
            "orders": orders,
        }
    )


# =========================================
# ORDER DETAIL PAGE
# =========================================

def order_detail(request, order_id):

    user_id = get_logged_in_user_id(request)

    if not user_id:

        return redirect("login")

    # =========================================
    # GET ORDER
    # =========================================

    try:

        order = OrderService.get_order(
            order_id
        )

    except Exception:

        return redirect("/my-orders/")

    if not order:

        return redirect("/my-orders/")

    # =========================================
    # CHECK ORDER OWNER
    # =========================================

    if order.user_id != user_id:

        return redirect("/my-orders/")

    # =========================================
    # CANCEL REQUEST
    # =========================================

    if request.method == "POST":

        action = request.POST.get(
            "action"
        )

        if action == "cancel":

            return cancel_order(
                request,
                order_id
            )

    # =========================================
    # GET ORDER ITEMS
    # =========================================

    order_items = OrderItemService.get_order_items(
        order_id
    )

    # =========================================
    # CALCULATE SUBTOTAL
    # =========================================

    for item in order_items:

        item.subtotal = (
            item.price
            * item.quantity
        )

    # =========================================
    # DISPLAY ORDER DETAIL
    # =========================================

    return render(
        request,
        "shop/order_detail.html",
        {
            "order": order,
            "order_items": order_items,
        }
    )


# =========================================
# CANCEL ORDER
# =========================================

def cancel_order(request, order_id):

    user_id = get_logged_in_user_id(request)

    if not user_id:

        return redirect("login")

    if request.method != "POST":

        return redirect(
            "order_detail",
            order_id=order_id
        )

    # =========================================
    # GET ORDER
    # =========================================

    try:

        order = OrderService.get_order(
            order_id
        )

    except Exception:

        return redirect("/my-orders/")

    if not order:

        return redirect("/my-orders/")

    # =========================================
    # CHECK ORDER OWNER
    # =========================================

    if order.user_id != user_id:

        return redirect("/my-orders/")

    # =========================================
    # ONLY PLACED / CONFIRMED CAN CANCEL
    # =========================================

    if order.order_status not in [
        "PLACED",
        "CONFIRMED"
    ]:

        messages.error(
            request,
            "This order cannot be cancelled."
        )

        return redirect(
            "order_detail",
            order_id=order_id
        )

    # =========================================
    # CANCEL ORDER
    # =========================================

    try:

        with transaction.atomic():

            order_items = OrderItemService.get_order_items(
                order_id
            )

            # =========================================
            # RESTORE STOCK
            # =========================================

            for item in order_items:

                variant = ProductVariantService.get_variant(
                    item.variant_id
                )

                new_stock = (
                    variant.stock_quantity
                    + item.quantity
                )

                ProductVariantService.update_variant(

                    variant.variant_id,

                    stock_quantity=new_stock
                )

            # =========================================
            # UPDATE ORDER STATUS
            # =========================================

            OrderService.update_order(

                order_id,

                order_status="CANCELLED"
            )

        messages.success(
            request,
            "Your order has been cancelled successfully."
        )

    except Exception:

        messages.error(
            request,
            "Unable to cancel the order."
        )

    return redirect(
        "order_detail",
        order_id=order_id
    )


# =========================================
# WISHLIST
# =========================================

def wishlist(request):

    user_id = get_logged_in_user_id(request)

    if not user_id:

        return redirect("login")

    wishlist_items = WishlistService.get_wishlist_by_user(
        user_id
    )

    return render(
        request,
        "shop/wishlist.html",
        {
            "wishlist_items": wishlist_items,
        }
    )


# =========================================
# ADD / REMOVE WISHLIST
# =========================================

def toggle_wishlist(request, product_id):

    user_id = get_logged_in_user_id(request)

    if not user_id:

        return redirect("login")

    if request.method == "POST":

        WishlistService.toggle_wishlist(
            user_id,
            product_id
        )

    return redirect(
        "product_detail",
        product_id=product_id
    )


# =========================================
# REGISTER
# =========================================

def register(request):

    if request.session.get("user_id"):

        return redirect("home")

    if request.method == "POST":

        full_name = request.POST.get(
            "full_name",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        phone = request.POST.get(
            "phone",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )

        address_line1 = request.POST.get(
            "address_line1",
            ""
        ).strip()

        address_line2 = request.POST.get(
            "address_line2",
            ""
        ).strip()

        city = request.POST.get(
            "city",
            ""
        ).strip()

        state = request.POST.get(
            "state",
            ""
        ).strip()

        pincode = request.POST.get(
            "pincode",
            ""
        ).strip()

        # =========================================
        # REQUIRED FIELD VALIDATION
        # =========================================

        if not full_name:

            messages.error(
                request,
                "Please enter your full name."
            )

            return redirect("register")

        if not email:

            messages.error(
                request,
                "Please enter your email."
            )

            return redirect("register")

        if not phone:

            messages.error(
                request,
                "Please enter your phone number."
            )

            return redirect("register")

        if not password:

            messages.error(
                request,
                "Please enter a password."
            )

            return redirect("register")

        if password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return redirect("register")

        if not address_line1:

            messages.error(
                request,
                "Please enter your address."
            )

            return redirect("register")

        if not city:

            messages.error(
                request,
                "Please enter your city."
            )

            return redirect("register")

        if not state:

            messages.error(
                request,
                "Please enter your state."
            )

            return redirect("register")

        if not pincode:

            messages.error(
                request,
                "Please enter your pincode."
            )

            return redirect("register")

        # =========================================
        # PHONE VALIDATION
        # =========================================

        if (
            not phone.isdigit()
            or len(phone) != 10
        ):

            messages.error(
                request,
                "Please enter a valid 10-digit phone number."
            )

            return redirect("register")

        # =========================================
        # PINCODE VALIDATION
        # =========================================

        if (
            not pincode.isdigit()
            or len(pincode) != 6
        ):

            messages.error(
                request,
                "Please enter a valid 6-digit pincode."
            )

            return redirect("register")

        # =========================================
        # CREATE USER
        # =========================================

        try:

            user = UserService.register_user(

                full_name=full_name,

                email=email,

                password=password,

                phone=phone,

                address_line1=address_line1,

                address_line2=address_line2 or None,

                city=city,

                state=state,

                pincode=pincode,

                created_at=timezone.now()
            )

        except ValueError as error:

            messages.error(
                request,
                str(error)
            )

            return redirect("register")

        # =========================================
        # LOGIN AFTER REGISTRATION
        # =========================================

        request.session["user_id"] = user.user_id

        request.session["user_name"] = user.full_name

        messages.success(
            request,
            "Registration successful. Welcome to BHAVIKA!"
        )

        return redirect("home")

    return render(
        request,
        "shop/register.html"
    )


# =========================================
# LOGIN
# =========================================

def login_view(request):

    if request.session.get("user_id"):

        return redirect("home")

    if request.method == "POST":

        email = request.POST.get(
            "email",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        if not email:

            messages.error(
                request,
                "Please enter your email."
            )

            return redirect("login")

        if not password:

            messages.error(
                request,
                "Please enter your password."
            )

            return redirect("login")

        user = UserService.login_user(
            email,
            password
        )

        if user:

            request.session["user_id"] = user.user_id

            request.session["user_name"] = user.full_name

            messages.success(
                request,
                f"Welcome back, {user.full_name}!"
            )

            if user.is_admin:

                return redirect("admin_dashboard")

            return redirect("home")

        messages.error(
            request,
            "Invalid email or password."
        )

        return redirect("login")

    return render(
        request,
        "shop/login.html"
    )


# =========================================
# LOGOUT
# =========================================

def logout_view(request):

    request.session.flush()

    return redirect("home")


# =========================================
# USER PROFILE
# =========================================

def profile(request):

    user_id = request.session.get("user_id")

    # =========================================
    # USER MUST BE LOGGED IN
    # =========================================

    if not user_id:

        return redirect("login")

    # =========================================
    # GET USER
    # =========================================

    try:

        user = UserService.get_user(
            user_id
        )

    except Exception:

        request.session.flush()

        return redirect("login")

    if not user:

        request.session.flush()

        return redirect("login")

    # =========================================
    # UPDATE PROFILE
    # =========================================

    if request.method == "POST":

        full_name = request.POST.get(
            "full_name",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        phone = request.POST.get(
            "phone",
            ""
        ).strip()

        address_line1 = request.POST.get(
            "address_line1",
            ""
        ).strip()

        address_line2 = request.POST.get(
            "address_line2",
            ""
        ).strip()

        city = request.POST.get(
            "city",
            ""
        ).strip()

        state = request.POST.get(
            "state",
            ""
        ).strip()

        pincode = request.POST.get(
            "pincode",
            ""
        ).strip()

        # =========================================
        # VALIDATE REQUIRED FIELDS
        # =========================================

        if not full_name:

            messages.error(
                request,
                "Please enter your full name."
            )

            return redirect("profile")

        if not email:

            messages.error(
                request,
                "Please enter your email."
            )

            return redirect("profile")

        if not phone:

            messages.error(
                request,
                "Please enter your phone number."
            )

            return redirect("profile")

        if not address_line1:

            messages.error(
                request,
                "Please enter your address."
            )

            return redirect("profile")

        if not city:

            messages.error(
                request,
                "Please enter your city."
            )

            return redirect("profile")

        if not state:

            messages.error(
                request,
                "Please enter your state."
            )

            return redirect("profile")

        if not pincode:

            messages.error(
                request,
                "Please enter your pincode."
            )

            return redirect("profile")

        # =========================================
        # PHONE VALIDATION
        # =========================================

        if (
            not phone.isdigit()
            or len(phone) != 10
        ):

            messages.error(
                request,
                "Please enter a valid 10-digit phone number."
            )

            return redirect("profile")

        # =========================================
        # PINCODE VALIDATION
        # =========================================

        if (
            not pincode.isdigit()
            or len(pincode) != 6
        ):

            messages.error(
                request,
                "Please enter a valid 6-digit pincode."
            )

            return redirect("profile")

        # =========================================
        # UPDATE USER
        # =========================================

        try:

            user = UserService.update_user(

                user_id,

                full_name=full_name,

                email=email,

                phone=phone,

                address_line1=address_line1,

                address_line2=address_line2,

                city=city,

                state=state,

                pincode=pincode,
            )

            request.session["user_name"] = user.full_name

            messages.success(
                request,
                "Your profile has been updated successfully."
            )

            return redirect("profile")

        except ValueError as error:

            messages.error(
                request,
                str(error)
            )

            return redirect("profile")

        except Exception:

            messages.error(
                request,
                "Unable to update your profile. "
                "Email or phone may already be in use."
            )

            return redirect("profile")

    # =========================================
    # DISPLAY PROFILE
    # =========================================

    return render(
        request,
        "shop/profile.html",
        {
            "user": user,
        }
    )


# =========================================
# ADMIN DASHBOARD
# =========================================

def admin_dashboard(request):

    admin_user = get_admin_user(request)

    if not admin_user:

        messages.error(
            request,
            "You do not have permission to access the Admin Panel."
        )

        return redirect("home")

    # =========================================
    # TOTAL USERS
    # =========================================

    total_users = User.objects.count()

    # =========================================
    # TOTAL PRODUCTS
    # =========================================

    total_products = Product.objects.count()

    # =========================================
    # TOTAL ORDERS
    # =========================================

    total_orders = Order.objects.count()

    # =========================================
    # TOTAL SALES
    # =========================================

    total_sales = 0

    orders = Order.objects.all()

    for order in orders:

        if order.order_status != "CANCELLED":

            total_sales += order.total_amount

    # =========================================
    # ORDER STATUS COUNTS
    # =========================================

    placed_orders = Order.objects.filter(
        order_status="PLACED"
    ).count()

    confirmed_orders = Order.objects.filter(
        order_status="CONFIRMED"
    ).count()

    shipped_orders = Order.objects.filter(
        order_status="SHIPPED"
    ).count()

    out_for_delivery_orders = Order.objects.filter(
        order_status="OUT FOR DELIVERY"
    ).count()

    delivered_orders = Order.objects.filter(
        order_status="DELIVERED"
    ).count()

    cancelled_orders = Order.objects.filter(
        order_status="CANCELLED"
    ).count()

    # =========================================
    # RECENT ORDERS
    # =========================================

    recent_orders = Order.objects.select_related(
        "user"
    ).order_by(
        "-order_date"
    )[:5]

    # =========================================
    # DISPLAY DASHBOARD
    # =========================================

    return render(
        request,
        "shop/admin_dashboard.html",
        {
            "admin_user": admin_user,

            "total_users": total_users,

            "total_products": total_products,

            "total_orders": total_orders,

            "total_sales": total_sales,

            "placed_orders": placed_orders,

            "confirmed_orders": confirmed_orders,

            "shipped_orders": shipped_orders,

            "out_for_delivery_orders": out_for_delivery_orders,

            "delivered_orders": delivered_orders,

            "cancelled_orders": cancelled_orders,

            "recent_orders": recent_orders,
        }
    )


# =========================================
# ADMIN ORDERS
# =========================================

def admin_orders(request):

    admin_user = get_admin_user(request)

    if not admin_user:

        messages.error(
            request,
            "You do not have permission to access the Admin Panel."
        )

        return redirect("home")

    orders = OrderService.get_all_orders()

    return render(
        request,
        "shop/admin_orders.html",
        {
            "orders": orders,
            "admin_user": admin_user,
        }
    )


# =========================================
# ADMIN ORDER STATUS UPDATE
# =========================================

def admin_update_order_status(request, order_id):

    admin_user = get_admin_user(request)

    if not admin_user:

        messages.error(
            request,
            "You do not have permission to perform this action."
        )

        return redirect("home")

    if request.method != "POST":

        return redirect("admin_orders")

    # =========================================
    # GET ORDER
    # =========================================

    try:

        order = OrderService.get_order(
            order_id
        )

    except Exception:

        messages.error(
            request,
            "Order not found."
        )

        return redirect("admin_orders")

    if not order:

        messages.error(
            request,
            "Order not found."
        )

        return redirect("admin_orders")

    # =========================================
    # GET NEW STATUS
    # =========================================

    new_status = request.POST.get(
        "order_status",
        ""
    ).strip()

    valid_statuses = [
        "PLACED",
        "CONFIRMED",
        "SHIPPED",
        "OUT FOR DELIVERY",
        "DELIVERED",
        "CANCELLED",
    ]

    if new_status not in valid_statuses:

        messages.error(
            request,
            "Invalid order status."
        )

        return redirect("admin_orders")

    # =========================================
    # CANCELLED CANNOT BE UPDATED
    # =========================================

    if order.order_status == "CANCELLED":

        messages.error(
            request,
            "Cancelled orders cannot be updated."
        )

        return redirect("admin_orders")

    # =========================================
    # DELIVERED CANNOT BE UPDATED
    # =========================================

    if order.order_status == "DELIVERED":

        messages.error(
            request,
            "Delivered orders cannot be updated."
        )

        return redirect("admin_orders")

    # =========================================
    # STATUS FLOW
    # =========================================

    status_flow = [
        "PLACED",
        "CONFIRMED",
        "SHIPPED",
        "OUT FOR DELIVERY",
        "DELIVERED",
    ]

    current_status = order.order_status

    # =========================================
    # CANCEL ORDER
    # =========================================

    if new_status == "CANCELLED":

        if current_status not in [
            "PLACED",
            "CONFIRMED"
        ]:

            messages.error(
                request,
                "This order cannot be cancelled at this stage."
            )

            return redirect("admin_orders")

        try:

            with transaction.atomic():

                order_items = OrderItemService.get_order_items(
                    order_id
                )

                # =========================================
                # RESTORE STOCK
                # =========================================

                for item in order_items:

                    variant = ProductVariantService.get_variant(
                        item.variant_id
                    )

                    new_stock = (
                        variant.stock_quantity
                        + item.quantity
                    )

                    ProductVariantService.update_variant(
                        variant.variant_id,
                        stock_quantity=new_stock
                    )

                # =========================================
                # UPDATE STATUS
                # =========================================

                OrderService.update_order(
                    order_id,
                    order_status="CANCELLED"
                )

            messages.success(
                request,
                f"Order #{order_id} has been cancelled."
            )

        except Exception:

            messages.error(
                request,
                "Unable to cancel the order."
            )

        return redirect("admin_orders")

    # =========================================
    # CHECK CURRENT STATUS
    # =========================================

    if current_status not in status_flow:

        messages.error(
            request,
            "Current order status is invalid."
        )

        return redirect("admin_orders")

    # =========================================
    # GET STATUS INDEX
    # =========================================

    current_index = status_flow.index(
        current_status
    )

    new_index = status_flow.index(
        new_status
    )

    # =========================================
    # PREVENT BACKWARD STATUS
    # =========================================

    if new_index != current_index + 1:

        messages.error(
            request,
            f"Order must move from "
            f"{current_status} to the next stage."
        )

        return redirect("admin_orders")

    # =========================================
    # UPDATE STATUS
    # =========================================

    OrderService.update_order(
        order_id,
        order_status=new_status
    )

    messages.success(
        request,
        f"Order #{order_id} status "
        f"updated to {new_status}."
    )

    return redirect("admin_orders")


# =========================================
# ADMIN PRODUCT MANAGEMENT
# =========================================

def admin_products(request):

    admin_user = get_admin_user(request)

    if not admin_user:

        messages.error(
            request,
            "You do not have permission to access the Admin Panel."
        )

        return redirect("home")

    products = Product.objects.select_related(
        "category"
    ).order_by(
        "-product_id"
    )

    return render(
        request,
        "shop/admin_products.html",
        {
            "products": products,
            "admin_user": admin_user,
        }
    )


# =========================================
# ADMIN ADD PRODUCT
# =========================================

def admin_add_product(request):

    admin_user = get_admin_user(request)

    if not admin_user:

        messages.error(
            request,
            "You do not have permission to access the Admin Panel."
        )

        return redirect("home")

    categories = Category.objects.all().order_by(
        "category_name"
    )

    if request.method == "POST":

        category_id = request.POST.get(
            "category_id",
            ""
        ).strip()

        product_name = request.POST.get(
            "product_name",
            ""
        ).strip()

        description = request.POST.get(
            "description",
            ""
        ).strip()

        price = request.POST.get(
            "price",
            ""
        ).strip()

        brand = request.POST.get(
            "brand",
            ""
        ).strip()

        # =========================================
        # IMAGE PATH
        # =========================================

        image_url = request.POST.get(
            "image_url",
            ""
        ).strip()

        gender = request.POST.get(
            "gender",
            ""
        ).strip()

        product_type = request.POST.get(
            "product_type",
            ""
        ).strip()

        stock_quantity = request.POST.get(
            "stock_quantity",
            ""
        ).strip()

        size = request.POST.get(
            "size",
            ""
        ).strip()

        # =========================================
        # REQUIRED FIELD VALIDATION
        # =========================================

        if not category_id:

            messages.error(
                request,
                "Please select a category."
            )

            return redirect("admin_add_product")

        if not product_name:

            messages.error(
                request,
                "Please enter product name."
            )

            return redirect("admin_add_product")

        if not description:

            messages.error(
                request,
                "Please enter product description."
            )

            return redirect("admin_add_product")

        if not price:

            messages.error(
                request,
                "Please enter product price."
            )

            return redirect("admin_add_product")

        if not image_url:

            messages.error(
                request,
                "Please enter the image path."
            )

            return redirect("admin_add_product")

        if not size:

            messages.error(
                request,
                "Please enter product size."
            )

            return redirect("admin_add_product")

        if not stock_quantity:

            messages.error(
                request,
                "Please enter stock quantity."
            )

            return redirect("admin_add_product")

        # =========================================
        # GET CATEGORY
        # =========================================

        try:

            category = Category.objects.get(
                category_id=category_id
            )

        except Category.DoesNotExist:

            messages.error(
                request,
                "Selected category does not exist."
            )

            return redirect("admin_add_product")

        # =========================================
        # VALIDATE PRICE
        # =========================================

        try:

            price_value = float(price)

            if price_value < 0:

                messages.error(
                    request,
                    "Price cannot be negative."
                )

                return redirect("admin_add_product")

        except ValueError:

            messages.error(
                request,
                "Please enter a valid price."
            )

            return redirect("admin_add_product")

        # =========================================
        # VALIDATE STOCK
        # =========================================

        try:

            stock_value = int(stock_quantity)

            if stock_value < 0:

                messages.error(
                    request,
                    "Stock quantity cannot be negative."
                )

                return redirect("admin_add_product")

        except ValueError:

            messages.error(
                request,
                "Please enter a valid stock quantity."
            )

            return redirect("admin_add_product")

        # =========================================
        # SAVE PRODUCT
        # =========================================

        try:

            product = Product.objects.create(

                category=category,

                product_name=product_name,

                description=description,

                price=price_value,

                brand=brand or None,

                image_url=image_url,

                product_type=product_type or None,

                gender=gender or None,

                is_active=True,

                created_at=timezone.now()
            )

            # =========================================
            # CREATE FIRST VARIANT
            # =========================================

            ProductVariant.objects.create(

                product=product,

                size=size,

                stock_quantity=stock_value
            )

            messages.success(
                request,
                f"{product_name} has been added successfully."
            )

            return redirect("admin_products")

        except Exception:

            messages.error(
                request,
                "Unable to add product."
            )

            return redirect("admin_add_product")

    return render(
        request,
        "shop/admin_add_product.html",
        {
            "categories": categories,
        }
    )


# =========================================
# ADMIN EDIT PRODUCT
# =========================================

def admin_edit_product(request, product_id):

    admin_user = get_admin_user(request)

    if not admin_user:

        messages.error(
            request,
            "You do not have permission to access the Admin Panel."
        )

        return redirect("home")

    # =========================================
    # GET PRODUCT
    # =========================================

    try:

        product = Product.objects.get(
            product_id=product_id
        )

    except Product.DoesNotExist:

        messages.error(
            request,
            "Product not found."
        )

        return redirect("admin_products")

    categories = Category.objects.all().order_by(
        "category_name"
    )

    # =========================================
    # UPDATE PRODUCT
    # =========================================

    if request.method == "POST":

        category_id = request.POST.get(
            "category_id",
            ""
        ).strip()

        product_name = request.POST.get(
            "product_name",
            ""
        ).strip()

        description = request.POST.get(
            "description",
            ""
        ).strip()

        price = request.POST.get(
            "price",
            ""
        ).strip()

        brand = request.POST.get(
            "brand",
            ""
        ).strip()

        # =========================================
        # IMAGE PATH
        # =========================================

        image_url = request.POST.get(
            "image_url",
            ""
        ).strip()

        gender = request.POST.get(
            "gender",
            ""
        ).strip()

        product_type = request.POST.get(
            "product_type",
            ""
        ).strip()

        # =========================================
        # REQUIRED FIELD VALIDATION
        # =========================================

        if not category_id:

            messages.error(
                request,
                "Please select a category."
            )

            return redirect(
                "admin_edit_product",
                product_id=product_id
            )

        if not product_name:

            messages.error(
                request,
                "Please enter product name."
            )

            return redirect(
                "admin_edit_product",
                product_id=product_id
            )

        if not description:

            messages.error(
                request,
                "Description is required."
            )

            return redirect(
                "admin_edit_product",
                product_id=product_id
            )

        if not price:

            messages.error(
                request,
                "Price is required."
            )

            return redirect(
                "admin_edit_product",
                product_id=product_id
            )

        if not image_url:

            messages.error(
                request,
                "Image path is required."
            )

            return redirect(
                "admin_edit_product",
                product_id=product_id
            )

        # =========================================
        # VALIDATE PRICE
        # =========================================

        try:

            price_value = float(price)

            if price_value < 0:

                messages.error(
                    request,
                    "Price cannot be negative."
                )

                return redirect(
                    "admin_edit_product",
                    product_id=product_id
                )

        except ValueError:

            messages.error(
                request,
                "Please enter a valid price."
            )

            return redirect(
                "admin_edit_product",
                product_id=product_id
            )

        # =========================================
        # GET CATEGORY
        # =========================================

        try:

            category = Category.objects.get(
                category_id=category_id
            )

        except Category.DoesNotExist:

            messages.error(
                request,
                "Selected category not found."
            )

            return redirect(
                "admin_edit_product",
                product_id=product_id
            )

        # =========================================
        # UPDATE PRODUCT
        # =========================================

        try:

            product.category = category

            product.product_name = product_name

            product.description = description

            product.price = price_value

            product.brand = brand or None

            product.image_url = image_url

            product.product_type = product_type or None

            product.gender = gender or None

            product.save(
                update_fields=[
                    "category",
                    "product_name",
                    "description",
                    "price",
                    "brand",
                    "image_url",
                    "product_type",
                    "gender"
                ]
            )

            messages.success(
                request,
                "Product updated successfully."
            )

            return redirect(
                "admin_products"
            )

        except Exception:

            messages.error(
                request,
                "Unable to update product."
            )

            return redirect(
                "admin_edit_product",
                product_id=product_id
            )

    # =========================================
    # DISPLAY EDIT PAGE
    # =========================================

    return render(
        request,
        "shop/admin_edit_product.html",
        {
            "product": product,
            "categories": categories,
        }
    )


# =========================================
# ADMIN ACTIVATE / DEACTIVATE PRODUCT
# =========================================

def admin_toggle_product(request, product_id):

    admin_user = get_admin_user(request)

    if not admin_user:

        messages.error(
            request,
            "You do not have permission to access the Admin Panel."
        )

        return redirect("home")

    if request.method != "POST":

        return redirect("admin_products")

    try:

        product = Product.objects.get(
            product_id=product_id
        )

        product.is_active = not product.is_active

        product.save(
            update_fields=["is_active"]
        )

        if product.is_active:

            messages.success(
                request,
                f"{product.product_name} has been activated."
            )

        else:

            messages.success(
                request,
                f"{product.product_name} has been deactivated."
            )

    except Product.DoesNotExist:

        messages.error(
            request,
            "Product not found."
        )

    return redirect("admin_products")


# =========================================
# ADMIN UPDATE VARIANT STOCK
# =========================================

def admin_update_stock(request, variant_id):

    admin_user = get_admin_user(request)

    if not admin_user:

        messages.error(
            request,
            "You do not have permission to access the Admin Panel."
        )

        return redirect("home")

    if request.method != "POST":

        return redirect("admin_products")

    try:

        variant = ProductVariant.objects.select_related(
            "product"
        ).get(
            variant_id=variant_id
        )

    except ProductVariant.DoesNotExist:

        messages.error(
            request,
            "Product variant not found."
        )

        return redirect("admin_products")

    stock_quantity = request.POST.get(
        "stock_quantity",
        ""
    ).strip()

    try:

        stock_value = int(stock_quantity)

        if stock_value < 0:

            messages.error(
                request,
                "Stock quantity cannot be negative."
            )

            return redirect("admin_products")

        variant.stock_quantity = stock_value

        variant.save(
            update_fields=["stock_quantity"]
        )

        messages.success(
            request,
            f"Stock updated for "
            f"{variant.product.product_name}."
        )

    except ValueError:

        messages.error(
            request,
            "Please enter a valid stock quantity."
        )

    return redirect("admin_products")