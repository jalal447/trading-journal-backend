from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Trade

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'full_name', 'subscription_plan', 'account_size', 'risk_per_trade_percent')
        read_only_fields = ('subscription_plan',)

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'full_name', 'password', 'account_size', 'risk_per_trade_percent')

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            password=validated_data['password'],
            account_size=validated_data.get('account_size', 0),
            risk_per_trade_percent=validated_data.get('risk_per_trade_percent', 1)
        )
        return user

class TradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trade
        fields = '__all__'
        read_only_fields = ('user', 'rr_planned', 'pnl', 'created_at')
