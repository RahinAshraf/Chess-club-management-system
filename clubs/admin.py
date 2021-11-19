"""Configuration of the admin interface"""
from django.contrib import admin
from .models import User, MembershipType

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for users."""

    list_display = [
        "email","first_name","last_name","date_joined"
    ]

@admin.register(MembershipType)
class UserAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for MembershipType."""

    list_display = [
        "user","type"
    ]
