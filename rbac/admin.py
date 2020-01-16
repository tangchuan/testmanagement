from django.contrib import admin

# Register your models here.
from django.contrib.auth.hashers import make_password

from rbac.adminforms import UserAdminForm
from rbac.models import Menu, Permission, Role, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username','email','realname','phone', 'created_time')
    form = UserAdminForm

    filter_horizontal = ('role',)

    def save_model(self, request, obj, form, change):
        obj.password = make_password(obj.password)
        return super(UserAdmin, self).save_model(request, obj, form, change)

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    filter_horizontal = ('permission',)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'parent', 'menu']


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['priority','title', ]