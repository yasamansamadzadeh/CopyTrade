# -*- encoding: utf-8 -*-

from django.urls import path

from .views import masters

urlpatterns = [
    path('masters/', masters, name="masters"),
]
