from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('refresh-token/', views.refresh_token, name='refresh-token'),
    path('password-reset/', views.request_password_reset, name='request-password-reset'),
    path('password-reset-confirm/', views.reset_password, name='reset-password'),
    path('edit-profile/', views.edit_profile, name='edit-profile'),
    path('change-password/', views.change_password, name='change-password'),
    path('logout/', views.logout, name='logout'),   
    path('google-login/', views.GoogleLogin.as_view(), name='google-login'),
]