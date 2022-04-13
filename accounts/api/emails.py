from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from helpers.classes import EmailThread
from bpproject.settings import DEFAULT_FROM_EMAIL, URL


def confirmation_email(new_user):
    token = PasswordResetTokenGenerator().make_token(new_user)
    uid = urlsafe_base64_encode(force_bytes(new_user.id))
    message = render_to_string('emails/confirmation_email.html',
                               {'url': f'{URL}api/accounts/email-verification/{uid}/{token}'})
    EmailThread('Email confirmation', message, new_user.email, f'Poslito <{DEFAULT_FROM_EMAIL}>').start()
