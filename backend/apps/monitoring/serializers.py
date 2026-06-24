from rest_framework import serializers
from .models import MonitoringRule, Alert, CompetitorWatch, MarketEvent


class MonitoringRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonitoringRule
        fields = [
            'id', 'name', 'rule_type', 'area', 'developer', 'compound',
            'property_type', 'min_price', 'max_price', 'price_change_threshold_pct',
            'notification_channels', 'webhook_url', 'is_active',
            'created_at', 'last_triggered_at',
        ]
        read_only_fields = ['id', 'created_at', 'last_triggered_at']


class AlertSerializer(serializers.ModelSerializer):
    rule_name = serializers.CharField(source='rule.name', read_only=True)

    class Meta:
        model = Alert
        fields = [
            'id', 'rule_name', 'title', 'message', 'severity',
            'metadata', 'is_read', 'created_at',
        ]


class CompetitorWatchSerializer(serializers.ModelSerializer):
    developer_name = serializers.CharField(source='developer.name', read_only=True)
    developer_slug = serializers.CharField(source='developer.slug', read_only=True)

    class Meta:
        model = CompetitorWatch
        fields = ['id', 'developer', 'developer_name', 'developer_slug', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']


class MarketEventSerializer(serializers.ModelSerializer):
    area_name = serializers.CharField(source='area.name', read_only=True, allow_null=True)
    developer_name = serializers.CharField(source='developer.name', read_only=True, allow_null=True)

    class Meta:
        model = MarketEvent
        fields = [
            'id', 'event_type', 'title', 'description', 'area_name',
            'developer_name', 'impact_score', 'detected_at',
        ]
