from django.urls import path
from .views import panel_admin

urlpatterns = [
    path('paneladmin/', panel_admin, name='panel_admin'),
]
