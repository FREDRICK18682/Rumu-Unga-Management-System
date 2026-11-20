from django.urls import path
from .views import humanresource_view

app_name = "hr"

urlpatterns = [
    path("", humanresource_view, name="index"),
]