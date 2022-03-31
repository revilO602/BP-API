from django.urls import path

from accounts.api.views import AccountsView, AccountDetailView, mail
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

app_name = 'accounts'

urlpatterns = [
    path('<str:account_id>', AccountDetailView.as_view(), name="accounts"),
    path('', AccountsView.as_view(), name="account_detail"),

    path('mail/', mail, name="mail"),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
