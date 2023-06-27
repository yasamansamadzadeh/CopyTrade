from django.contrib import admin

from .models import *


@admin.register(Trader)
class TraderAdmin(admin.ModelAdmin):
    pass


class FollowInline(admin.TabularInline):
    model = FollowSymbol
    extra = 1


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    inlines = (FollowInline, )


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    pass


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'status')
