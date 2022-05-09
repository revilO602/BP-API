from django.utils.translation import gettext_lazy as _
from django import forms
from django.contrib.auth.forms import PasswordResetForm

from accounts.models import Account


class MyPasswordResetForm(PasswordResetForm):
    """
    Custom password reset form to ensure users get retrieved from the database properly.
    """
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )

    def get_users(self, email):
        """
        Retrieve all users that match the given email and are active from the database.

        :param email: email of users to retrieve
        :return: list of account model instances
        """
        active_users = Account.objects.filter(is_active=True, email=email)
        return (
            u
            for u in active_users
            if u.has_usable_password()
        )
