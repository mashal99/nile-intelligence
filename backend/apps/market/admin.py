from django.contrib import admin
from .models import MarketSnapshot, CompoundSnapshot, DeveloperMetrics, MarketInsight


@admin.register(MarketSnapshot)
class MarketSnapshotAdmin(admin.ModelAdmin):
    list_display = ['area', 'property_type', 'date', 'avg_price', 'active_listings']
    list_filter = ['property_type', 'date']
    search_fields = ['area__name']


@admin.register(CompoundSnapshot)
class CompoundSnapshotAdmin(admin.ModelAdmin):
    list_display = ['compound', 'date', 'avg_price', 'active_listings']
    search_fields = ['compound__name']


@admin.register(MarketInsight)
class MarketInsightAdmin(admin.ModelAdmin):
    list_display = ['title', 'insight_type', 'area', 'tokens_used', 'generated_at']
    list_filter = ['insight_type']
    search_fields = ['title']
    readonly_fields = ['tokens_used', 'generated_at', 'ai_model']
