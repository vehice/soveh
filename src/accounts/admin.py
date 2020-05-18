from django.contrib import admin
from .models import UserProfile, Profile
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from django import forms

admin.site.unregister(Group)

class ProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil de Usuario'
    fk_name = 'user'
    exclude = ('role', 'state', 'confirmation_code')

class CustomUserProfile(UserAdmin):
    inlines = (ProfileInline, )
    fieldsets = (
            (None, {'fields': ('email', 'password', 'username', 'first_name', 'last_name', 'is_active')}),
        )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'userprofile')

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserProfile, self).get_inline_instances(request, obj)

    def save_model(self, request, obj, form, change):
        super(CustomUserProfile, self).save_model(request, obj, form, change)

admin.site.unregister(User)
admin.site.register(User, CustomUserProfile)
