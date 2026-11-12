from django.urls import path
from .views import (
    inventory_view, 
    UngaBalesInventoryAPIView, 
    CompanyMachineryInventoryAPIView,
    set_bales_stock,
    get_machinary_list,
    update_companymachinery
)

app_name = 'inventory'

urlpatterns = [
    path('', inventory_view, name='index'),
    path('api/ungabales/', UngaBalesInventoryAPIView.as_view(), name='api-ungabales'),
    path('api/companymachinery/', CompanyMachineryInventoryAPIView.as_view(), name='api-companymachinery'),
    path('api/stock/', set_bales_stock, name='api_bales_stock'),
    path('api/machinary/', get_machinary_list, name='api_companymachinary_list'),
    path('api/companymachinery/<int:pk>/', update_companymachinery, name='api_companymachinery_update'),
]