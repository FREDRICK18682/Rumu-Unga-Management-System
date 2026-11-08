from django.urls import path
from .views import procurement_view, MaizeProcurementAPIView, PackagingProcurementAPIView

urlpatterns = [
    path('procurement/', procurement_view, name='procurement-page'),

    path('api/maize/', MaizeProcurementAPIView.as_view(), name='api-maize'),
    path('api/packaging/', PackagingProcurementAPIView.as_view(), name='api-packaging'),
]