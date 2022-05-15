import json

from django.urls import reverse
from django.utils.http import urlencode
from rest_framework import status
from rest_framework.test import APITestCase

sample_account = {
    "email": "test@test.com",
    "password": "Testovacie123",
    "first_name": "Jozef",
    "last_name": "Mrkva",
    "phone_number": "0905265859"
}

sample_account_2 = {
    "email": "test2@test.com",
    "password": "Testovacie456",
    "first_name": "Marian",
    "last_name": "Mrkva",
    "phone_number": "0905265859"
}

sample_courier = {
    "id_number": 123,
    "id_expiration_date": "2022-03-18",
    "dl_number": 456,
    "dl_expiration_date": "2022-03-18",
    "vehicle_type": "large",
    "home_address": "Vilova 23, 85101 Bratislava"
}

sample_delivery_1 = {
    "receiver.email": "test@test.com",
    "receiver.first_name": "Jozef",
    "receiver.last_name": "Mrkva",
    "receiver.phone_number": "0905265859",
    "item.name": "Ponozky",
    "item.description": "Krasne zlte ponozky",
    "pickup_place.place_id": "ChIJl2HKCjaJbEcRaEOI_YKbH2M",
    "pickup_place.formatted_address": "Vilova 23, Presov 85101, Slovakia",
    "pickup_place.country": "Slovakia",
    "pickup_place.city": "Presov",
    "pickup_place.street_address": "Vilova 23",
    "pickup_place.postal_code": "85101",
    "pickup_place.latitude": 49.097275508021475,
    "pickup_place.longitude": 20.10818515071519,
    "delivery_place.place_id": "ChIJe5XGZxvgPkcR0IuXxtH3AAQ",
    "delivery_place.formatted_address": "Dacova 14, Kosice 12345, Austria",
    "delivery_place.country": "Austria",
    "delivery_place.city": "Kosice",
    "delivery_place.street_address": "Dacova 14",
    "delivery_place.postal_code": "12345",
    "delivery_place.latitude": 48.14263867939738,
    "delivery_place.longitude": 17.09862408609207,
}

sample_delivery_2 = sample_delivery_1.copy()
sample_delivery_2['item.name'] = 'dalej'
sample_delivery_2['pickup_place.place_id'] = 'ChIJL9SKbuM9FUcRMpCLC4o_Ivg'
sample_delivery_2['pickup_place.latitude'] = 48.82618178064965
sample_delivery_2['pickup_place.longitude'] = 19.14428963143319,


class TestRegisterCourier(APITestCase):
    """ Test registering as courier """

    def register(self):
        self.client.post(reverse('account_api:accounts'), sample_account)

    def authenticate(self):
        credentials = {
            "password": sample_account['password'],
            "email": sample_account['email'],
        }
        response = self.client.post(reverse('account_api:token_obtain_pair'), credentials)
        token = response.data['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_post(self):
        self.register()
        self.authenticate()
        response = self.client.post(reverse('couriers_api:couriers'), sample_courier)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['vehicle_type'], 'large')


class TestClosestDeliveries(APITestCase):
    """ Test getting a list of closest deliveries """

    def prepare(self):
        self.client.post(reverse('account_api:accounts'), sample_account)
        self.client.post(reverse('account_api:accounts'), sample_account_2)
        self.authenticate_1()
        self.post()
        self.authenticate_2()
        self.client.post(reverse('couriers_api:couriers'), sample_courier)

    def authenticate_1(self):
        credentials = {
            "password": sample_account['password'],
            "email": sample_account['email'],
        }
        response = self.client.post(reverse('account_api:token_obtain_pair'), credentials)
        token = response.data['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def authenticate_2(self):
        credentials = {
            "password": sample_account_2['password'],
            "email": sample_account_2['email'],
        }
        response = self.client.post(reverse('account_api:token_obtain_pair'), credentials)
        token = response.data['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def post(self):
        self.client.post(reverse('core_api:deliveries'), sample_delivery_1)
        self.client.post(reverse('core_api:deliveries'), sample_delivery_2)

    def test_get(self):
        self.prepare()
        response = self.client.get(f'{reverse("couriers_api:closest_deliveries")}'
                                   f'?{urlencode({"lat": 48.42568196973426, "lon": 17.583197128156495})}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['item']['name'], 'Ponozky')
        self.assertEqual(response.data[0]['state'], 'ready')


class TestAcceptDelivery(APITestCase):
    """ Test starting delivery with sending message over WS"""

    def prepare(self):
        self.client.post(reverse('account_api:accounts'), sample_account)
        self.client.post(reverse('account_api:accounts'), sample_account_2)
        self.authenticate_1()
        self.post()
        self.authenticate_2()
        self.client.post(reverse('couriers_api:couriers'), sample_courier)
        return self.client.get(f'{reverse("couriers_api:closest_deliveries")}'
                               f'?{urlencode({"lat": 48.42568196973426, "lon": 17.583197128156495})}').data[0][
            'safe_id']

    def authenticate_1(self):
        credentials = {
            "password": sample_account['password'],
            "email": sample_account['email'],
        }
        response = self.client.post(reverse('account_api:token_obtain_pair'), credentials)
        token = response.data['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def authenticate_2(self):
        credentials = {
            "password": sample_account_2['password'],
            "email": sample_account_2['email'],
        }
        response = self.client.post(reverse('account_api:token_obtain_pair'), credentials)
        self.token = response.data['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def post(self):
        self.client.post(reverse('core_api:deliveries'), sample_delivery_1)
        self.client.post(reverse('core_api:deliveries'), sample_delivery_2)

    def test_accept(self):
        safe_id = self.prepare()
        response = self.client.patch(reverse('core_api:delivery_state', kwargs={'safe_delivery_id': safe_id}),
                                     json.dumps({"state": "assigned"}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)