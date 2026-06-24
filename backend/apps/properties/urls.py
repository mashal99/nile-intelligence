from django.urls import path
from . import views

urlpatterns = [
    path('', views.PropertyListView.as_view(), name='property-list'),
    path('<int:pk>/', views.PropertyDetailView.as_view(), name='property-detail'),
    path('developers/', views.DeveloperListView.as_view(), name='developer-list'),
    path('developers/<slug:slug>/', views.DeveloperDetailView.as_view(), name='developer-detail'),
    path('areas/', views.AreaListView.as_view(), name='area-list'),
    path('compounds/', views.CompoundListView.as_view(), name='compound-list'),
    path('compounds/compare/', views.CompoundCompareView.as_view(), name='compound-compare'),
    path('compounds/<slug:slug>/', views.CompoundDetailView.as_view(), name='compound-detail'),
    path('compounds/<slug:slug>/listings/', views.CompoundListingsView.as_view(), name='compound-listings'),
]
