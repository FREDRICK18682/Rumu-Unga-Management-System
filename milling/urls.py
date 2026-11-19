from django.urls import path
from .views import milling_view, LocalMillingAPIView, SchoolMillRecordsAPIView

app_name = 'milling'

urlpatterns = [
    path('', milling_view, name='index'),
    path('api/local-milling/', LocalMillingAPIView.as_view(), name="api-local-milling"),
    path('api/school-millrecords/', SchoolMillRecordsAPIView.as_view(), name="api-school-millrecords"),
]