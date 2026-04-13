from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display  = ("username", "email", "rol", "is_active")
    list_filter   = ("rol",)
    fieldsets     = UserAdmin.fieldsets + (
        ("Rol InvPro", {"fields": ("rol",)}),
    )