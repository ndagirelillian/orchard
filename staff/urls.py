from django.urls import path
from . import views

urlpatterns = [
    path('staff/', views.staff_list, name='staff_list'),
    path('staff/add/', views.add_staff, name='add_staff'),
    path('staff/<int:pk>/', views.staff_detail, name='staff_detail'),
    path('staff/<int:pk>/edit/', views.edit_staff, name='edit_staff'),
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/mark/', views.mark_attendance, name='mark_attendance'),
    path('attendance/checkout/<int:pk>/', views.checkout_attendance, name='checkout_attendance'),
]
