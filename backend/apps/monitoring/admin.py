from django.contrib import admin
from .models import MonitoringRule, Alert, CompetitorWatch, MarketEvent


@admin.register(MonitoringRule)
class MonitoringRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'rule_type', 'is_active', 'last_triggered_at']
    list_filter = ['rule_type', 'is_active']
    search_fields = ['name', 'user__email']
    raw_id_fields = ['user', 'area', 'developer', 'compound']


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['title', 'rule', 'severity', 'is_read', 'is_sent', 'created_at']
    list_filter = ['severity', 'is_read', 'is_sent']
    search_fields = ['title', 'rule__name']


@admin.register(MarketEvent)
class MarketEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'area', 'impact_score', 'detected_at']
    list_filter = ['event_type']
    search_fields = ['title']
