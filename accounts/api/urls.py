from django.urls import path
from accounts.api.views import (AccountsView, AccountDetailView,
                                resend_confirmation_email, email_verification, MyTokenObtainPairView)
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'accounts'

urlpatterns = [
    path('verification_email/<str:uid>/<str:token>/', email_verification, name="email_verification"),
    path('verification_email/', resend_confirmation_email, name="resend_confirmation_email"),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('<str:account_id>/', AccountDetailView.as_view(), name="account_detail"),
    path('', AccountsView.as_view(), name="accounts"),
]
