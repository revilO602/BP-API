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


class TestRegister(APITestCase):
    """ Test registering """
    def test_register(self):
        response = self.client.post(reverse('account_api:accounts'), sample_account)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class TestAuth(APITestCase):
    """ Test authentication """
    def register(self):
        self.client.post(reverse('account_api:accounts'), sample_account)

    def test_auth(self):
        self.register()
        credentials = {
            "password": sample_account['password'],
            "email": sample_account['email'],
        }
        response = self.client.post(reverse('account_api:token_obtain_pair'), credentials)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestGet(APITestCase):
    """ Test retrieving user account info """
    expected_result = {
        "email": "test@test.com",
        "first_name": "Jozef",
        "last_name": "Mrkva",
        "phone_number": "0905265859",
        "courier": None
    }

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

    def test_get(self):
        self.register()
        self.authenticate()
        response = self.client.get(reverse('account_api:account_detail', kwargs={'account_id': 'me'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.expected_result)


class TestPatch(APITestCase):
    """ Test updating user account """
    expected_result = {
        "email": "test@test.com",
        "first_name": "Marian",
        "last_name": "Mrkva",
        "phone_number": "0905265859",
        "courier": None
    }

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

    def test_patch(self):
        self.register()
        self.authenticate()
        response = self.client.patch(reverse('account_api:account_detail', kwargs={'account_id': 'me'}),
                                     {'first_name': 'Marian'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.expected_result)