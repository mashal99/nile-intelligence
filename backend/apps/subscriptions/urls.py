from django.urls import path
from . import views

urlpatterns = [
    path('', views.CurrentSubscriptionView.as_view(), name='subscription-current'),
    path('usage/', views.UsageView.as_view(), name='subscription-usage'),
    path('plans/', views.PlansView.as_view(), name='subscription-plans'),
    path('upgrade/', views.UpgradePlanView.as_view(), name='subscription-upgrade'),
    path('invoices/', views.InvoiceListView.as_view(), name='subscription-invoices'),
]
