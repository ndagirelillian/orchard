from django.contrib import admin
from .models import Setting, Profile

# Register your models here.
admin.site.register(Setting)

@admin.register(Profile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']
