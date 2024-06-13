from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace="accounts")),
    path('polls/', include('polls.urls', namespace="polls")),
    path('social-auth/', include('social_django.urls', namespace="social")),
]
