from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework import serializers
from django.core.exceptions import ValidationError

from user_accounts.models import Account

from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})



class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = Account
        fields = ['username', 'password', 'email', 'first_name', 'last_name', ]

    def validate_email(self, value):
        """
        Validate email field.
        """
        if Account.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def create(self, validated_data):
        """
        Create a new user.
        """
        validated_data['username'] = validated_data['email']
        user = Account.objects.create_user(**validated_data)
        return user



class UserReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = ['username', 'email', 'first_name', 'last_name', 'role']
        read_only_fields = fields