from django.urls import path
from .views import (procurement_view, 
                MaizeProcurementAPIView, 
                PackagingProcurementAPIView, 
                get_stock_summary,
                UpdateStockAPIView,
                PapersByTypeSummaryAPIView
                )
app_name = 'procurement'
urlpatterns = [
    path('', procurement_view, name='index'),

    path('api/maize/', MaizeProcurementAPIView.as_view(), name='api-maize'),
    path('api/packaging/', PackagingProcurementAPIView.as_view(), name='api-packaging'),
    path('api/stock/', get_stock_summary, name='api_stock_summary'),
    path('api/update-stock/', UpdateStockAPIView.as_view(), name='update-stock'),
    path("api/papers-by-type/", PapersByTypeSummaryAPIView.as_view(), name="papers-by-type"),
]