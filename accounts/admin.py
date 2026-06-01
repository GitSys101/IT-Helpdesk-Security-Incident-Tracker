from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'role', 'job_title', 'department', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Professional Info', {'fields': ('role', 'job_title', 'employee_id', 'department')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Professional Info', {'fields': ('role', 'job_title', 'employee_id', 'department')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
