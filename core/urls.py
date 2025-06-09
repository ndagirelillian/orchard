from django.urls import path
from . import views
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('logout', views.logout_func, name='logout'),
    path('logoutpage', views.logout_page, name='logoutpage'),
    path('api_register/', RegisterView.as_view(), name='register'),
    path('api_login/', LoginView.as_view(), name='login'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/create/', UserCreateView.as_view(), name='user-create'),
    path('users/<int:pk>/edit/', UserUpdateView.as_view(), name='user-update'),
]