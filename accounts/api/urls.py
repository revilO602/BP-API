from django.urls import path
from accounts.api.views import (AccountsView, AccountDetailView,
                                resend_confirmation_email, email_verification, MyTokenObtainPairView)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

app_name = 'accounts'

urlpatterns = [
    path('email-verification/<str:uid>/<str:token>', email_verification, name="email_verification"),
    path('confirmation-email', resend_confirmation_email, name="resend_confirmation_email"),
    path('<str:account_id>', AccountDetailView.as_view(), name="accounts"),
    path('', AccountsView.as_view(), name="account_detail"),

    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh')
]
