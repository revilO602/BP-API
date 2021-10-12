from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from account.models import Account, Person
from django.db import transaction


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ['email', 'first_name', 'last_name', 'phone_number']


class AccountSerializer(serializers.ModelSerializer):
    # password = serializers.CharField(write_only=True, validators=[validate_password])
    person = PersonSerializer(partial=True)

    class Meta:
        model = Account
        fields = ['email', 'password', 'person']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    @transaction.atomic
    def create(self, validated_data):
        person_data = validated_data.pop('person')
        person = Person.objects.create(**person_data)
        account = Account.objects.create(
            email=validated_data['email'],
            person=person
        )
        account.set_password(validated_data['password'])
        person.save()
        account.save()
        return account

    @transaction.atomic
    def update(self, instance, validated_data):
        this_person = instance.person
        if validated_data.get('person'):
            person_data = validated_data.pop('person')
            this_person.email = person_data.get('email', this_person.email)
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


