from django.urls import path

from account.api.views import(
        AccountRegistrationView,
        AccountView,
    )
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

app_name = 'account'

urlpatterns = [
    path('register/', AccountRegistrationView.as_view(), name="register"),
    path('my_account/', AccountView.as_view(), name="my_account"),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
