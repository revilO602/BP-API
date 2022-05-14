import logging

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from helpers.classes import EmailThread
from bpproject.settings import DEFAULT_FROM_EMAIL, URL

logger = logging.getLogger('poslito')

def verification_email(new_user):
    """
    Send a verification email to new user with an activation link.

    :param new_user: The account object of the newly created user
    :return: None
    """
    token = PasswordResetTokenGenerator().make_token(new_user)
    uid = urlsafe_base64_encode(force_bytes(new_user.id))
    message = render_to_string('emails/confirmation_email.html',
                               {'url': f'{URL}api/accounts/verification_email/{uid}/{token}'})
    EmailThread('Email confirmation', message, new_user.email, f'Poslito <{DEFAULT_FROM_EMAIL}>').start()
