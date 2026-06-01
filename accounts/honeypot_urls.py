from django.urls import path
from . import honeypot_views

urlpatterns = [
    path('', honeypot_views.fake_admin_login, name='fake_admin_login'),
    path('<path:url>', honeypot_views.fake_admin_login, name='fake_admin_catchall'),
]
