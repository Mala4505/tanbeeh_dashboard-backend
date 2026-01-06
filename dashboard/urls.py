from django.urls import path
from .views import *

urlpatterns = [
    path("bootstrap/", dashboard_bootstrap),
]
