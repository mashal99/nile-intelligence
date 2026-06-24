from django.urls import path
from . import views

urlpatterns = [
    path('', views.ReportListCreateView.as_view(), name='reports'),
    path('<int:pk>/', views.ReportDetailView.as_view(), name='report-detail'),
    path('<int:pk>/download/', views.ReportDownloadView.as_view(), name='report-download'),
]
