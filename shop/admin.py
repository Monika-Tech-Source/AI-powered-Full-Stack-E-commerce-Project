from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'order_id',
        'user',
        'order_date',
        'total_amount',
        'payment_method',
        'order_status',
    )

    list_filter = (
        'order_status',
        'payment_method',
    )

    search_fields = (
        'order_id',
        'user__email',
        'user__full_name',
    )

    ordering = (
        '-order_date',
    )