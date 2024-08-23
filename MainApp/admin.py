from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Transaction

class CustomUserAdmin(UserAdmin):
    # Add the 'amount' field to the fieldsets to include it in the User detail page
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('amount',)}),
    )

    # Display the 'amount' field in the list view
    list_display = UserAdmin.list_display + ('amount',)

admin.site.register(CustomUser, CustomUserAdmin)

# Register the Transaction model
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('type', 'amount', 'party', 'date', 'comment')
    list_filter = ('type', 'date')
    search_fields = ('party__username', 'comment')
    date_hierarchy = 'date'

admin.site.register(Transaction, TransactionAdmin)
