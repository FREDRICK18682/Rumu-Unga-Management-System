from django.urls import path
from .views import milling_view
app_name = 'milling'

urlpatterns = [
    path('', milling_view, name='index'),
]