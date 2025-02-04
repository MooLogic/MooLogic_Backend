from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^signup/$', views.signup, name='signup'),
    re_path(r'^login/$', views.login, name='login'),
    re_path(r'^test/$', views.test_api, name='test'),
]