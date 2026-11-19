from django.urls import path
from . import views
from .views import sale_home, PaidBalesRecordsAPIView, RecordsOfUnpaidBalesAPIView, DailySalesSummeryAPiView, SendBalesToInventoryAPIView

app_name = 'sale'  

urlpatterns = [
    path('', views.sale_home, name='home'),  
    path('api/paid-bales/', PaidBalesRecordsAPIView.as_view(), name='api-paid-bales'),
    path('api/unpaid-bales/', RecordsOfUnpaidBalesAPIView.as_view(), name='api-unpaid-bales'),
    path('api/daily-summary/', DailySalesSummeryAPiView.as_view(), name='api-daily-summary' ),
    path(
        "api/send-bales-to-inventory/",
        SendBalesToInventoryAPIView.as_view(),
        name="send-bales-to-inventory",
    ),
]