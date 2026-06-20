from django.urls import path
from .views import home, analyse, recommend

urlpatterns = [
    path("", home),
    path("analyse/", analyse),
    path("recommend/", recommend),
]