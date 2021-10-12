from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from account.models import Account, Person


class AccountAdmin(UserAdmin):
    exclude = ('username',)
    fieldsets = (
        ('Personal info', {'fields': ('email', 'password')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    ordering = ('email',)
    list_display = ('email',
                    'date_joined', 'last_login', 'is_admin', 'is_staff')
    search_fields = ('email',)
    readonly_fields = ('date_joined', 'last_login',)
    filter_horizontal = ()
    list_filter = ()


admin.site.register(Account, AccountAdmin)
admin.site.register(Person)
