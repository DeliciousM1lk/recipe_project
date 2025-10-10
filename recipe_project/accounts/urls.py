from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from .views import (
    register,
    profile,
    activate,
    CustomPasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView,
    confirm_email_change,
    resend_activation_email,
    resend_email_change_email,
)

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    path('profile/', profile, name='profile'),
    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='accounts/password_change_form.html',
        success_url=reverse_lazy('profile')
    ), name='password_change'),

    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('resend_activation_email/', resend_activation_email, name='resend_activation_email'),

    path('confirm_email/<uidb64>/<token>/', confirm_email_change, name='confirm_email_change'),
    path('resend_email_change_email/', resend_email_change_email, name='resend_email_change_email'),

    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]