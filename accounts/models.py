from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import pgcrypto
from couriers.models import Courier
from helpers.models import TrackingModel
import uuid


class AccountManager(BaseUserManager):
    """
    Account manager responsible for creating account instances through the CLI.
    """
    def create_user(self, email, password):
        """
        Create a normal user.

        :param email: Email of new user
        :param password: Plain text password of new user
        :return: Created account instance
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            password=password,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Create a superuser.

        :param email: Email of new superuser
        :param password: Plain text password of new superuser
        :return: Created account instance
        """
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user


class Person(TrackingModel):
    """
    Person model responsible for holding personal data of people.
    * All personal data is encrypted on the database level.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = pgcrypto.EncryptedCharField(models.CharField(max_length=60))
    last_name = pgcrypto.EncryptedCharField(models.CharField(max_length=60))
    phone_number = pgcrypto.EncryptedCharField(models.CharField(max_length=15))
    email = pgcrypto.EncryptedEmailField(verbose_name="email", max_length=60)

    class Meta:
        db_table = "person"

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)


class Account(AbstractBaseUser, TrackingModel):
    """
    Account model responsible for holding credentials of users.
    * All personal data is encrypted on the database level.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = pgcrypto.EncryptedEmailField(verbose_name="email", max_length=60, unique=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    person = models.ForeignKey(Person, related_name='account', on_delete=models.CASCADE, null=True) # null because of admin/superuser - required in serializer
    courier = models.ForeignKey(Courier, related_name='account', on_delete=models.CASCADE, null=True)

    USERNAME_FIELD = 'email'

    objects = AccountManager()

    class Meta:
        db_table = "account"

    # For checking permissions. to keep it simple all admin have ALL permissons
    def has_perm(self, perm, obj=None):
        return self.is_admin

    # Does this user have permission to view this app? (ALWAYS YES FOR SIMPLICITY)
    def has_module_perms(self, app_label):
        return True
