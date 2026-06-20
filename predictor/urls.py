from django.urls import path
from .views import home, analyse

urlpatterns = [
    path("", home),
    path("analyse/", analyse),
]