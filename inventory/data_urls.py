from django.urls import path
from . import data_views as views

urlpatterns = [
    # Category URLs
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/add/', views.CategoryCreateView.as_view(), name='category-add'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category-edit'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category-delete'),

    # MenuItem URLs
    path('menu-items/', views.MenuItemListView.as_view(), name='menuitem-list'),
    path('menu-items/add/', views.MenuItemCreateView.as_view(), name='menuitem-add'),
    path('menu-items/<int:pk>/edit/', views.MenuItemUpdateView.as_view(), name='menuitem-edit'),
    path('menu-items/<int:pk>/delete/', views.MenuItemDeleteView.as_view(), name='menuitem-delete'),

    # DiningArea URLs
    path('dining-areas/', views.DiningAreaListView.as_view(), name='dining_area_list'),
    path('dining-area/create/', views.DiningAreaCreateView.as_view(), name='create_dining_area'),
    path('dining-area/<int:pk>/update/', views.DiningAreaUpdateView.as_view(), name='update_dining_area'),
    path('dining-area/<int:pk>/delete/', views.DiningAreaDeleteView.as_view(), name='delete_dining_area'),
    path('table/create/<int:area_id>/', views.TableCreateView.as_view(), name='create_table'),
    path('table/<int:pk>/update/', views.TableUpdateView.as_view(), name='update_table'),
    
    # Table URLs
    path('tables/', views.TableListView.as_view(), name='table-list'),
    path('tables/add/', views.TableCreateView.as_view(), name='table-add'),
    path('tables/<int:pk>/edit/', views.TableUpdateView.as_view(), name='table-edit'),
    path('tables/<int:pk>/delete/', views.TableDeleteView.as_view(), name='table-delete'),
]
