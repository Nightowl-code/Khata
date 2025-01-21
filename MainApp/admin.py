from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Transaction, SiteSettings

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Add the 'amount' field to the fieldsets to include it in the User detail page
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('amount',)}),
    )

    # Display the 'amount' field in the list view
    list_display = UserAdmin.list_display + ('amount',)


# Register the Transaction model
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('type', 'amount', 'party', 'date', 'comment','running_total','sequence_number','created_by')
    list_filter = ('type', 'date','party')
    search_fields = ('party__username', 'comment')
    date_hierarchy = 'date'

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('is_site_available','superuser_login_url')
