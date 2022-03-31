from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
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

