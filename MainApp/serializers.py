from .models import Transaction, CustomUser
from rest_framework import serializers

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    party = serializers.CurrentUserDefault()
    
    class Meta:
        model = Transaction
        fields = '__all__'

