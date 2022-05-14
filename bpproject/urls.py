"""
bpproject URL Configuration
"""
from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView, RedirectView

from accounts.password_reset_form import MyPasswordResetForm

urlpatterns = [
    path('admin/', admin.site.urls),

    # REST FRAMEWORK URLS
    path('api/deliveries/', include('deliveries.api.urls', 'core_api')),
    path('api/accounts/', include('accounts.api.urls', 'account_api')),
    path('api/routes/', include('routes.api.urls', 'routes_api')),
    path('api/couriers/', include('couriers.api.urls', 'couriers_api')),

    # PASSWORD RESET
    path('reset_password/', auth_views.PasswordResetView.as_view(
        template_name='accounts/registration/password_reset.html',
        email_template_name='emails/password_reset_email.html',
        success_url=reverse_lazy('password_reset_done'),  form_class=MyPasswordResetForm), name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/registration/password_reset_complete.html'), name='password_reset_complete'),

    # DOCS
    path('api/asyncapi/', TemplateView.as_view(template_name='wsdocs.html')),
    path('api/', RedirectView.as_view(url='https://app.swaggerhub.com/apis-docs/revilO602/Poslito/1.0.0', permanent=True)),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)