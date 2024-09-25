from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import customer, itemvariant, orderitem, salesorder, customuser, centreddata, adddata, supplier, deliverynote, invoicenote, retour

admin.site.register(salesorder)
admin.site.register(itemvariant)
admin.site.register(customer)
admin.site.register(orderitem)
admin.site.register(centreddata)
admin.site.register(adddata)
admin.site.register(supplier)
admin.site.register(deliverynote)
admin.site.register(invoicenote)
admin.site.register(retour)


# Define customuserAdmin class
class customuserAdmin(UserAdmin):
    model = customuser
    list_display = ('username', 'email', 'is_staff', 'is_superuser')
    search_fields = ('email', 'username')
    ordering = ('username',)
    
    # Required fields for the UserAdmin class
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('full_name',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'full_name', 'password1', 'password2'),
        }),
    )
    
    filter_horizontal = ()
    
    list_filter = ('is_active', 'is_staff', 'is_superuser')


# Register the customuser model with the custom admin interface
admin.site.register(customuser, customuserAdmin)