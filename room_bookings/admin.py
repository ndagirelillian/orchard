from django.contrib import admin
from .models import (
     RoomType,
    HotelBranch, Room, Customer, RoomReservation, SaunaUser, Sauna_services
)


@admin.register(Sauna_services)
class Sauner_serviceAdmin(admin.ModelAdmin):
    list_display=['name', 'description', 'price',]
    search_fields=['name',]


@admin.register(SaunaUser)
class SaunaUserAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'gender',
                    'service', 'keys', 'price', 'order_date']
    search_fields = ['customer_name', 'gender',  'service', 'order_date']




@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_price']
    search_fields = ['name']

@admin.register(HotelBranch)
class HotelBranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'country']
    search_fields = ['name', 'city']

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'room_type', 'hotel', 'is_available', 'capacity']
    list_filter = ['room_type', 'hotel', 'is_available']
    search_fields = ['room_number', 'room_type__name', 'hotel__name']

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'phone_number']
    search_fields = ['first_name', 'last_name', 'email']

@admin.register(RoomReservation)
class RoomReservationAdmin(admin.ModelAdmin):
    list_display = ['reservation_id', 'room', 'customer', 'check_in_date', 'check_out_date', 'status']
    list_filter = ['check_in_date', 'check_out_date', 'status']
    search_fields = ['reservation_id', 'customer__first_name', 'customer__last_name']
