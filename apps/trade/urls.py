# -*- encoding: utf-8 -*-

from django.urls import path

from .views import *

urlpatterns = [
    path('masters/', masters, name="masters"),
    path('orders/', orders, name="orders"),
]
