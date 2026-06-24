from django.urls import path
from . import views

urlpatterns = [
    path('rules/', views.MonitoringRuleListCreateView.as_view(), name='monitoring-rules'),
    path('rules/<int:pk>/', views.MonitoringRuleDetailView.as_view(), name='monitoring-rule-detail'),
    path('alerts/', views.AlertListView.as_view(), name='alerts'),
    path('alerts/<int:pk>/read/', views.AlertMarkReadView.as_view(), name='alert-mark-read'),
    path('alerts/read-all/', views.AlertMarkAllReadView.as_view(), name='alert-mark-all-read'),
    path('competitors/', views.CompetitorWatchListView.as_view(), name='competitor-watch'),
    path('events/', views.MarketEventListView.as_view(), name='market-events'),
]
