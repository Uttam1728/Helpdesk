from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework import serializers
from django.core.exceptions import ValidationError

from user_accounts.models import Account

from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})



class AccountWriteSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = Account
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name', 'role' ]
        read_only_fields = ['id']

    def validate_email(self, value):
        """
        Validate email field.
        """
        acc_qs = Account.objects.filter(email=value)
        if self.instance:
            acc_qs = acc_qs.exclude(pk=self.instance.pk)
        if acc_qs.exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def create(self, validated_data):
        """
        Create a new user.
        """
        validated_data['username'] = validated_data['email']
        # user = super().create(validated_data)
        user = Account.objects.create_user(**validated_data)
        return user


class AccountReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']
        read_only_fields = fields