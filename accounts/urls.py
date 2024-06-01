from django.urls import path
from django.contrib.auth import views as auth_views
from .views import index, register, admin_dashboard, admin_approve, user_settings, update_profile, change_password, Login, Logout, activate, account_activation_sent

urlpatterns = [
    path("", index, name="index"),
    path('register/', register, name="register"),
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin_approve/<int:user_id>/', admin_approve, name='admin_approve'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('account_activation_sent/', account_activation_sent, name='account_activation_sent'),
    path("settings/", user_settings, name="settings"),
    path("update_profile/", update_profile, name="update_profile"),
    path("change_password/", change_password, name="change_password"),
    path("login/", Login, name="login"),
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='password_reset_form.html',
        email_template_name='password_reset_email.html',
        subject_template_name='password_reset_subject.txt',
        success_url='/password_reset/done/'
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password_reset_confirm.html',
        success_url='/reset/done/'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password_reset_complete.html'
    ), name='password_reset_complete'),
    path("logout/", Logout, name="logout"),
]

