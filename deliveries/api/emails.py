from django.template.loader import render_to_string
from helpers.classes import EmailThread
from bpproject.settings import DEFAULT_FROM_EMAIL, URL


def delivery_start_receiver_email(delivery):
    message = render_to_string('emails/receiver_delivery_start_email.html',
                               {'sender_name': delivery.sender.first_name,
                                'item_name': delivery.item.name,
                                'delivery_place': delivery.delivery_place.formatted_address,
                                'receiver_number': delivery.receiver.phone_number})
    EmailThread('You have a package on the way', message, delivery.receiver.email,
                f'Poslito <{DEFAULT_FROM_EMAIL}>').start()
