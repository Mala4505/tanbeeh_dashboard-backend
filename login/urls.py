from django.urls import path
from .views import login_view, me_view, all_users_view

urlpatterns = [
    path('login/', login_view),
    path('me/', me_view),
    path('users/all/', all_users_view),
]
