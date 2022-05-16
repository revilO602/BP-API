from django.template.loader import render_to_string
from helpers.classes import EmailThread
from bpproject.settings import DEFAULT_FROM_EMAIL, URL


def delivery_start_receiver_email(delivery):
    """
    Sends an email to the delivery receiver, informing them of the delivery.

    :param delivery: the new delivery object
    """
    message = render_to_string('emails/receiver_delivery_start_email.html',
                               {'sender_first_name': delivery.sender.first_name,
                                'sender_last_name': delivery.sender.last_name,
                                'sender_email': delivery.sender.email,
                                'sender_phone': delivery.sender.phone_number,
                                'receiver_first_name': delivery.receiver.first_name,
                                'receiver_last_name': delivery.receiver.last_name,
                                'receiver_email': delivery.receiver.email,
                                'receiver_phone': delivery.receiver.phone_number,
                                'item_name': delivery.item.name,
                                'item_description': delivery.item.description,
                                'pickup_place': delivery.pickup_place.formatted_address,
                                'delivery_place': delivery.delivery_place.formatted_address}
                               )
    EmailThread('You have a package on the way', message, delivery.receiver.email,
                f'Poslito <{DEFAULT_FROM_EMAIL}>').start()


def delivery_end_sender_email(delivery):
    """
    Sends an email to the delivery sender, informing them of the end of the delivery.

    :param delivery: delivery object
    """
    message = render_to_string('emails/sender_delivery_start_email.html',
                               {'sender_first_name': delivery.sender.first_name,
                                'sender_last_name': delivery.sender.last_name,
                                'sender_email': delivery.sender.email,
                                'sender_phone': delivery.sender.phone_number,
                                'receiver_first_name': delivery.receiver.first_name,
                                'receiver_last_name': delivery.receiver.last_name,
                                'receiver_email': delivery.receiver.email,
                                'receiver_phone': delivery.receiver.phone_number,
                                'item_name': delivery.item.name,
                                'item_description': delivery.item.description,
                                'pickup_place': delivery.pickup_place.formatted_address,
                                'delivery_place': delivery.delivery_place.formatted_address,
                                'courier_first_name': delivery.courier.person.first_name,
                                'courier_last_name': delivery.courier.person.last_name,
                                'courier_email': delivery.courier.person.email,
                                'courier_phone': delivery.courier.person.phone_number,
                                'delivery_price': str(delivery.price)}
                               )
    EmailThread('Your package was delivered', message, delivery.sender.email,
                f'Poslito <{DEFAULT_FROM_EMAIL}>').start()