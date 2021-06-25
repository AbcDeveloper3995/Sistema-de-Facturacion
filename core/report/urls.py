from django.urls import path

from core.report.views import ReportSaleView

urlpatterns = [
    # reports
    path('sale/', ReportSaleView.as_view(), name='sale_report'),
]