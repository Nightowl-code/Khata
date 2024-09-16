from .models import Transaction, CustomUser, SiteSettings
from rest_framework import serializers

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name','amount','amount_type',"is_active","block_date"]


class TransactionSerializer(serializers.ModelSerializer):
    party = CustomUserSerializer(read_only=True)
    date = serializers.DateField(format="%d-%m-%y")
    class Meta:
        model = Transaction
        fields = '__all__'


class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = '__all__'