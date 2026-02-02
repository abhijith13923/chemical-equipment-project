from django.urls import path
from .views import UploadCSV, EquipmentList, EquipmentSummary, UploadHistoryList, PressureTemperatureView, GeneratePDFReport

urlpatterns = [
     path('upload/', UploadCSV.as_view(), name='upload-csv'),
     path('list/',EquipmentList.as_view(), name='equipment-list'),
     path('summary/',EquipmentSummary.as_view(), name='equipment-summary'),
     path("history/", UploadHistoryList.as_view(), name="upload-history-list"),
     path("pressure-temperature/", PressureTemperatureView.as_view(), name="pressure-temperature"),
     path("report/pdf/", GeneratePDFReport.as_view(), name="generate-pdf-report"),


]