from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    DiningAreaViewSet,
    TableViewSet,
    OrderTransactionViewSet,
    OrderItemViewSet,
    CategoryViewSet,
    MenuItemViewSet,
    CurrentUserViewSet,
    DashboardStatsView,
)

router = DefaultRouter()
router.register(r'dining-areas', DiningAreaViewSet, basename='dining-area')
router.register(r'tables', TableViewSet, basename='table')
router.register(r'transactions', OrderTransactionViewSet, basename='transactions')
router.register(r'order-items', OrderItemViewSet, basename='order-items')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'menu-items', MenuItemViewSet, basename='menu-items')

urlpatterns = [
    path('', include(router.urls)),
    path('current-user/', CurrentUserViewSet.as_view(), name='current-user'),
    path('dashboard-stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
]
