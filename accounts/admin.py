from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models import Account, Person


class AccountAdmin(UserAdmin):
    exclude = ('username',)
    fieldsets = (
        ('Personal info', {'fields': ('email', 'password')}),
        ('Important dates', {'fields': ('created_at', 'updated_at')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    ordering = ('email',)
    list_display = ('email',
                    'created_at', 'updated_at', 'is_admin', 'is_staff')
    search_fields = ('email',)
    readonly_fields = ('created_at', 'updated_at',)
    filter_horizontal = ()
    list_filter = ()


admin.site.register(Account, AccountAdmin)
admin.site.register(Person)
