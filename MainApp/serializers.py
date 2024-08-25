from .models import Transaction, CustomUser
from rest_framework import serializers

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name','amount','amount_type']


class TransactionSerializer(serializers.ModelSerializer):
    party = CustomUserSerializer(read_only=True)
    
    class Meta:
        model = Transaction
        fields = '__all__'

