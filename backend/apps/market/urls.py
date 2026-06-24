from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.DashboardSummaryView.as_view(), name='market-dashboard'),
    path('heatmap/', views.AreaHeatmapView.as_view(), name='market-heatmap'),
    path('inventory/', views.InventorySummaryView.as_view(), name='market-inventory'),
    path('developer-rankings/', views.DeveloperRankingsView.as_view(), name='market-developer-rankings'),
    path('trends/<slug:area_slug>/', views.PriceTrendView.as_view(), name='market-price-trend'),
    path('insights/', views.MarketInsightListView.as_view(), name='market-insights'),
    path('insights/<int:pk>/', views.MarketInsightDetailView.as_view(), name='market-insight-detail'),
]
