from django.urls import path
from .views import (procurement_view, 
                MaizeProcurementAPIView, 
                PackagingProcurementAPIView, 
                get_stock_summary,
                update_stock_summary
                )
app_name = 'procurement'
urlpatterns = [
    path('', procurement_view, name='index'),

    path('api/maize/', MaizeProcurementAPIView.as_view(), name='api-maize'),
    path('api/packaging/', PackagingProcurementAPIView.as_view(), name='api-packaging'),
    path('api/stock/', get_stock_summary, name='api_stock_summary'),
    path('api/update-stock/', update_stock_summary, name='update-stock-summary'),
]