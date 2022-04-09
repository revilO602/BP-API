import json

from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync
from django.core.exceptions import ValidationError

from deliveries.models import Delivery
from helpers.enums import DeliveryState

FORMAT_ERROR_MESSAGE = {'errors': ["Incorrect position format, make sure the message is in the following format "
                                   "(-90 >= latitude <= 90, -180 >= longitude <= 180)"],
                        'expectedFormat': {
                            'latitude': 50.5258,
                            'longitude': 25.4568
                        }}


def get_delivery(delivery_id):
    delivery = Delivery.objects.get(id=delivery_id)
    return delivery

# Validate that message is valid position with coordinates
def validateMessage(message):
    try:
        lon = message['longitude']
        lat = message['latitude']
        if not (-90 <= lat <= 90):
            return False
        if not (-180 <= lon <= 180):
            return False
    except (KeyError, TypeError):
        return False
    return True

class CourierConsumer(JsonWebsocketConsumer):
    def connect(self):
        # Try to create a delivery group - if no delivery_id in url put into group_ALL
        try:
            self.group_id = self.scope['url_route']['kwargs']['delivery_id']
            self.group_name = 'group_%s' % self.group_id
        except KeyError:
            self.group_name = 'group_ALL'
        self.accept()
        if self.group_name == 'group_ALL':
            self.join_all_group()
        elif self.join_delivery_group():
            if self.delivery.courier == self.scope['user']:
                self.join_all_group()
        else:
            self.close()

    def join_delivery_group(self):
        try:
            # Try to join delivery group
            self.delivery = get_delivery(self.group_id)
            if not (self.delivery.state == DeliveryState.DELIVERING or self.delivery.state == DeliveryState.ASSIGNED):
                self.send_json({
                    'errors': ['Delivery is not being transported']
                })
                return False
            else:
                # Join delivery group
                async_to_sync(self.channel_layer.group_add)(
                    self.group_name,
                    self.channel_name
                )
                return True
        except Delivery.DoesNotExist:
            self.send_json({
                'errors': ['Delivery with given ID does not exist']
            })
            return False
        except ValidationError as e:
            self.send_json({
                'errors': e.messages
            })
            return False

    def join_all_group(self):
        # Join all group
        async_to_sync(self.channel_layer.group_add)(
            'group_ALL',
            self.channel_name
        )

    def disconnect(self, close_code):
        # Leave delivery group
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None, **kwargs):
        if text_data:
            try:
                self.receive_json(self.decode_json(text_data), **kwargs)
            except json.decoder.JSONDecodeError:
                self.send_json({'errors': ['Not a valid JSON']})
        else:
            self.send_json({
                'errors': ['Not text section in websocket message']
            })

    # Receive message from WebSocket
    def receive_json(self, content, **kwargs):
        user = self.scope["user"]
        if user.is_anonymous or not user.courier:
            self.send_json({
                'errors': ['Only courier can post to websocket']
            })
        elif self.group_name != 'group_ALL' and self.delivery.courier != user:
            self.send_json({
                'errors': ['Only courier of this delivery can post to websocket']
            })
        else:
            if not validateMessage(content):
                self.send_json(FORMAT_ERROR_MESSAGE)
                return
            # Send couriers position to delivery group
            async_to_sync(self.channel_layer.group_send)(
                self.group_name,
                {
                    'type': 'courier_position',
                    'message': content
                }
            )
            if self.group_name != 'group_ALL':
                # Send couriers position to group ALL
                async_to_sync(self.channel_layer.group_send)(
                    'group_ALL',
                    {
                        'type': 'courier_position',
                        'message': content
                    }
                )

    # Receive message from group
    def courier_position(self, event):
        content = event['message']
        content['courier_id'] = str(self.scope["user"].id)
        # Send message to WebSocket
        self.send_json(content)
