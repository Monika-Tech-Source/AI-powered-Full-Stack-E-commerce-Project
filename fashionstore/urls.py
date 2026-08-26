"""
URL configuration for fashionstore project.

The `urlpatterns` list routes URLs to views.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from shop import views


urlpatterns = [

    # =========================================
    # DJANGO ADMIN
    # =========================================

    path(
        "admin/",
        admin.site.urls
    ),

    # =========================================
    # HOME PAGE
    # =========================================

    path(
        "",
        views.home,
        name="home"
    ),

    # =========================================
    # SHOP APPLICATION
    # =========================================

    path(
        "",
        include("shop.urls")
    ),
]


# =========================================
# MEDIA FILES
# =========================================

if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )