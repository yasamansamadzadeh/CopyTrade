# -*- encoding: utf-8 -*-

from django.contrib import admin
from django.urls import path, include
from django.utils.translation import gettext_lazy as _

admin.site.site_header = _("Trader")
admin.site.site_title = _("Trader")
admin.site.index_title = _('Welcome to Administration Panel')

urlpatterns = [
    path('admin/', admin.site.urls),        # Django admin route
    path("", include("apps.myauth.urls")),    # Auth routes - login / register
    path("", include("apps.home.urls"))     # UI Kits Html files
]
