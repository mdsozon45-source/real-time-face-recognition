from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile, RecognizedFace

class CustomUserAdmin(UserAdmin):
    model = UserProfile
    # Define the fields to be displayed in the admin panel
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'image')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2')}
        ),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email')
    ordering = ('username',)

admin.site.register(UserProfile, CustomUserAdmin)
admin.site.register(RecognizedFace)
