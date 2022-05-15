from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

sample_account = {
    "email": "test@test.com",
    "password": "Testovacie123",
    "first_name": "Jozef",
    "last_name": "Mrkva",
    "phone_number": "0905265859"
}

sample_delivery = {
    "receiver.email": "test@test.com",
    "receiver.first_name": "Jozef",
    "receiver.last_name": "Mrkva",
    "receiver.phone_number": "0905265859",
    "item.name": "Ponozky",
    "item.description": "Krasne zlte ponozky",
    "pickup_place.place_id": "ChIJTQPgy2TtPkcRoFWXxtH3AAQ",
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


class TestCreate(APITestCase):
    """ Test creating delivery """

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
        response = self.client.post(reverse('core_api:deliveries'), sample_delivery)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class TestList(APITestCase):
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

    def post(self):
        self.client.post(reverse('core_api:deliveries'), sample_delivery)

    def test_get(self):
        self.register()
        self.authenticate()
        self.post()
        response = self.client.get(reverse('core_api:deliveries'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['state'], 'ready')
        self.assertEqual(response.data[0]['user_is'], 'sender')


class TestDetail(APITestCase):
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

    def post(self):
        return self.client.post(reverse('core_api:deliveries'), sample_delivery).data['id']

    def test_get(self):
        self.register()
        self.authenticate()
        delivery_id = self.post()
        self.client.credentials(HTTP_AUTHORIZATION='')
        response = self.client.get(reverse('core_api:delivery_detail', kwargs={'delivery_id': delivery_id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['state'], 'ready')


class TestPreview(APITestCase):
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
        response = self.client.post(reverse('core_api:deliveries_preview'), sample_delivery)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
