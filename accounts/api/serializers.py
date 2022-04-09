from abc import ABC

from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework import serializers, exceptions
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Account, Person

from couriers.api.serializers import CourierSerializer


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ['email', 'first_name', 'last_name', 'phone_number']


class AccountSerializer(serializers.ModelSerializer):
    # password = serializers.CharField(write_only=True, validators=[validate_password])
    first_name = serializers.CharField(max_length=60, source='person.first_name')
    last_name = serializers.CharField(max_length=60, source='person.last_name')
    phone_number = serializers.CharField(max_length=15, source='person.phone_number')
    courier = CourierSerializer(read_only=True, required=False)

    class Meta:
        model = Account
        fields = ['email', 'password', 'first_name', 'last_name', 'phone_number', 'courier']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        person = Person.objects.create(**validated_data.pop('person'), email=validated_data['email'])
        account = Account.objects.create(**validated_data, person=person)
        account.set_password(validated_data['password'])
        account.save()
        return account

    def update(self, instance, validated_data):
        this_person = instance.person
        if validated_data.get('person'):
            person_data = validated_data.pop('person')
            this_person.email = person_data.get('email', instance.email)
            this_person.first_name = person_data.get('first_name', this_person.first_name)
            this_person.last_name = person_data.get('last_name', this_person.last_name)
            this_person.phone_number = person_data.get('phone_number', this_person.phone_number)
            this_person.save()
        instance.email = validated_data.get('email', instance.email)
        instance.person = this_person
        new_password = validated_data.get('password')
        if new_password:
            instance.set_password(new_password)
        instance.save()
        return instance


class TokenObtainSerializerWithActiveCheck(TokenObtainSerializer):
    token_class = RefreshToken

    @classmethod
    def get_token(cls, user):
        return cls.token_class.for_user(user)

    def validate(self, attrs):
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            "password": attrs["password"],
        }
        try:
            authenticate_kwargs["request"] = self.context["request"]
        except KeyError:
            pass
        self.user = authenticate(**authenticate_kwargs)
        if not api_settings.USER_AUTHENTICATION_RULE(self.user):
            inactive_user = Account.objects.filter(email=authenticate_kwargs[self.username_field])
            if inactive_user and inactive_user[0].check_password(authenticate_kwargs["password"]):
                raise exceptions.AuthenticationFailed(
                    "Email not confirmed",
                    "no_active_account",
                )
            raise exceptions.AuthenticationFailed(
                self.error_messages["no_active_account"],
                "no_active_account",
            )

        refresh = self.get_token(self.user)
        data = {"refresh": str(refresh), "access": str(refresh.access_token)}
        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data