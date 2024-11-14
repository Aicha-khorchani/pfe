from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import customer,facture ,itemvariant,itemvariant,item,customuser,lead,leaddata, supplier,bonreception, retour , Command, Delivery , Stock

admin.site.register(item)
admin.site.register(itemvariant)
admin.site.register(customer)
admin.site.register(lead)
admin.site.register(leaddata)
admin.site.register(supplier)
admin.site.register(bonreception)
admin.site.register(facture)
admin.site.register(retour)
admin.site.register(Command)
admin.site.register(Delivery)
admin.site.register(Stock)




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