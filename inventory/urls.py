from django.urls import path
from .views import (
    inventory_view, 
    UngaBalesInventoryAPIView, 
    CompanyMachineryInventoryAPIView
)

app_name = 'inventory'

urlpatterns = [
    path('', inventory_view, name='index'),
    path('api/ungabales/', UngaBalesInventoryAPIView.as_view(), name='api-ungabales'),
    path('api/companymachinery/', CompanyMachineryInventoryAPIView.as_view(), name='api-companymachinery'),
]