from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from account.models import Account


class AccountSerializer(serializers.ModelSerializer):
   # password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = Account
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        account = Account.objects.create(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data['phone_number']
        )

        account.set_password(validated_data['password'])
        account.save()

        return account

    def update(self, instance, validated_data):
        new_password = validated_data['password']
        if new_password:
            validated_data['password'] = make_password(new_password)
            instance.set_password(validated_data['password'])
        return super().update(instance, validated_data)
