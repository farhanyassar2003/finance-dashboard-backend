from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Custom Fields", {"fields": ("role", "department", "updated_at")}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Custom Fields", {"fields": ("role", "department")}),
    )

    list_display = ("username", "email", "role","updated_at", "department", "is_active", "is_staff")
    list_filter = ("role", "department", "is_active", "is_staff")
    readonly_fields = ("updated_at",)