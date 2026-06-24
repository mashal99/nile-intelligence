from django.contrib import admin
from .models import Subscription, UsageRecord, Invoice


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'billing_cycle', 'is_active', 'started_at', 'expires_at']
    list_filter = ['plan', 'is_active', 'billing_cycle']
    search_fields = ['user__email']
    raw_id_fields = ['user']


@admin.register(UsageRecord)
class UsageRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'usage_type', 'count', 'date']
    list_filter = ['usage_type', 'date']
    search_fields = ['user__email']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['subscription', 'amount', 'currency', 'status', 'issued_at']
    list_filter = ['status', 'currency']
