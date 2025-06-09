from django.contrib import admin
from .models import Staff, StaffAttendance

# Register your models here.
admin.site.register(Staff)
admin.site.register(StaffAttendance)